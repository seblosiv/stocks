"""
Neurobird Search API client

Thin wrapper around the hosted Neurobird Search MCP endpoint
(https://search.neurobird.com/mcp), which speaks JSON-RPC 2.0 over HTTP POST.

Two capabilities are exposed:
    web_search   - live web search returning ranked results with page passages
                   already extracted, plus an optional grounded answer
    extract_url  - fetch one or more URLs as clean markdown / plain text

Auth is a bearer token. Get a free key (1,000 credits/month) with a single
unauthenticated call:

    python -c "import neurobird_search as n; print(n.create_api_key())"

then export it:

    export NEUROBIRD_KEY=nb_...
"""

import json
import os
import time
from typing import Dict, List, Optional

import requests

DEFAULT_BASE_URL = "https://search.neurobird.com"
DEFAULT_TIMEOUT = 60  # searches typically take 15-30s
MAX_RETRIES = 3


class NeurobirdError(Exception):
    """Base error for all Neurobird API failures"""


class NeurobirdAuthError(NeurobirdError):
    """Missing, invalid or exhausted API key"""


class NeurobirdRateLimitError(NeurobirdError):
    """Rate limited or out of credits"""


def get_api_key() -> Optional[str]:
    """Read the API key from the environment (NEUROBIRD_KEY or NEUROBIRD_API_KEY)"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv is optional; plain env vars still work
    return os.environ.get("NEUROBIRD_KEY") or os.environ.get("NEUROBIRD_API_KEY")


def create_api_key(base_url: str = DEFAULT_BASE_URL, timeout: int = 30) -> Dict:
    """
    Provision a new free API key. Requires no authentication.

    Returns:
        The raw response dict, which contains an 'api_key' field.
    """
    response = requests.post(f"{base_url.rstrip('/')}/keys", timeout=timeout)
    if response.status_code >= 400:
        raise NeurobirdError(
            f"Key provisioning failed ({response.status_code}): {response.text[:300]}"
        )
    return response.json()


def _parse_response(response: requests.Response) -> Dict:
    """
    Parse a JSON-RPC reply. The endpoint may answer with plain JSON or with an
    SSE stream (text/event-stream), so handle both.
    """
    content_type = response.headers.get("Content-Type", "")

    if "text/event-stream" not in content_type:
        try:
            return response.json()
        except ValueError as exc:
            raise NeurobirdError(
                f"Could not decode response: {response.text[:300]}"
            ) from exc

    # SSE: take the last data: frame that carries a JSON-RPC payload
    payload = None
    for line in response.text.splitlines():
        if not line.startswith("data:"):
            continue
        chunk = line[len("data:"):].strip()
        if not chunk or chunk == "[DONE]":
            continue
        try:
            candidate = json.loads(chunk)
        except ValueError:
            continue
        if isinstance(candidate, dict) and ("result" in candidate or "error" in candidate):
            payload = candidate

    if payload is None:
        raise NeurobirdError(f"No JSON-RPC payload in stream: {response.text[:300]}")
    return payload


def _unwrap_tool_result(result: Dict) -> Dict:
    """
    Turn an MCP tools/call result into a plain dict.

    Prefers structuredContent, then a JSON-encoded text block, and finally
    falls back to the raw text under a 'text' key.
    """
    if not isinstance(result, dict):
        return {"text": str(result)}

    if isinstance(result.get("structuredContent"), dict):
        return result["structuredContent"]

    texts = [
        block.get("text", "")
        for block in result.get("content", [])
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    joined = "\n".join(t for t in texts if t)

    if joined:
        try:
            parsed = json.loads(joined)
            if isinstance(parsed, dict):
                return parsed
            return {"results": parsed} if isinstance(parsed, list) else {"text": joined}
        except ValueError:
            return {"text": joined}

    return result


def normalize_results(payload: Dict) -> Dict:
    """
    Normalize a web_search payload into a predictable shape:

        {"answer": str | None, "results": [{"title", "url", "content", "score"}]}

    The API returns page passages rather than snippets, but key naming can vary
    by response mode, so accept the common aliases.
    """
    if not isinstance(payload, dict):
        return {"answer": None, "results": []}

    raw = payload.get("results") or payload.get("sources") or payload.get("data") or []
    if isinstance(raw, dict):
        raw = raw.get("results", [])
    if not isinstance(raw, list):
        raw = []

    results = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        results.append({
            "title": item.get("title") or item.get("name") or "Untitled",
            "url": item.get("url") or item.get("link") or "",
            "content": (
                item.get("content")
                or item.get("passage")
                or item.get("text")
                or item.get("snippet")
                or ""
            ),
            "score": item.get("score") or item.get("relevance_score"),
            "published": item.get("published_date") or item.get("published") or item.get("date"),
        })

    answer = payload.get("answer") or payload.get("grounded_answer")
    if isinstance(answer, dict):
        answer = answer.get("text") or answer.get("content")

    return {
        "answer": answer,
        "results": results,
        "quotes": payload.get("quotes") or [],
        "raw": payload,
    }


class NeurobirdClient:
    """Client for the Neurobird Search API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key or get_api_key()
        self.base_url = (base_url or os.environ.get("NEUROBIRD_BASE_URL")
                         or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self._session_id = None
        self._request_id = 0

    # -- plumbing ---------------------------------------------------------

    def _headers(self, authenticated: bool = True) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if authenticated:
            if not self.api_key:
                raise NeurobirdAuthError(
                    "No Neurobird API key. Set NEUROBIRD_KEY, or call "
                    "neurobird_search.create_api_key() to provision a free one."
                )
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        return headers

    def _rpc(self, method: str, params: Optional[Dict] = None,
             authenticated: bool = True) -> Dict:
        """Send a JSON-RPC request to the MCP endpoint and return its result"""
        self._request_id += 1
        body = {"jsonrpc": "2.0", "id": self._request_id, "method": method}
        if params is not None:
            body["params"] = params

        url = f"{self.base_url}/mcp"
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.post(
                    url,
                    headers=self._headers(authenticated),
                    json=body,
                    timeout=self.timeout,
                )
            except requests.RequestException as exc:
                last_error = NeurobirdError(f"Request to {url} failed: {exc}")
                time.sleep(2 ** attempt)
                continue

            # The server hands back a session id on the first call; echo it back.
            session_id = response.headers.get("Mcp-Session-Id")
            if session_id:
                self._session_id = session_id

            if response.status_code in (401, 403):
                raise NeurobirdAuthError(
                    f"Neurobird rejected the API key ({response.status_code}). "
                    "Check NEUROBIRD_KEY."
                )
            if response.status_code == 429:
                if attempt == MAX_RETRIES - 1:
                    raise NeurobirdRateLimitError(
                        "Rate limited or out of credits (HTTP 429)."
                    )
                time.sleep(2 ** attempt)
                continue
            if response.status_code >= 500:
                last_error = NeurobirdError(
                    f"Neurobird server error ({response.status_code})."
                )
                time.sleep(2 ** attempt)
                continue
            if response.status_code >= 400:
                raise NeurobirdError(
                    f"Neurobird request failed ({response.status_code}): "
                    f"{response.text[:300]}"
                )

            payload = _parse_response(response)
            if "error" in payload:
                error = payload["error"] or {}
                raise NeurobirdError(
                    f"Neurobird error {error.get('code', '')}: "
                    f"{error.get('message', 'unknown error')}".strip()
                )
            return payload.get("result", {})

        raise last_error or NeurobirdError("Request failed after retries")

    # -- API surface ------------------------------------------------------

    def list_tools(self) -> List[Dict]:
        """List the tools the server exposes (web_search, extract_url)"""
        result = self._rpc("tools/list", authenticated=False)
        return result.get("tools", [])

    def balance(self) -> Dict:
        """Remaining credits for the current key"""
        if not self.api_key:
            raise NeurobirdAuthError("No Neurobird API key configured.")
        response = self.session.get(
            f"{self.base_url}/balance",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30,
        )
        if response.status_code in (401, 403):
            raise NeurobirdAuthError("Neurobird rejected the API key.")
        if response.status_code >= 400:
            raise NeurobirdError(
                f"Balance lookup failed ({response.status_code}): {response.text[:200]}"
            )
        return response.json()

    def web_search(
        self,
        query: str,
        search_depth: str = "standard",
        max_results: int = 6,
        include_answer: bool = True,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        days: Optional[int] = None,
        topic: str = "general",
    ) -> Dict:
        """
        Search the live web.

        Args:
            query: the search query
            search_depth: basic | standard | advanced (advanced costs 2 credits)
            max_results: 1-20
            include_answer: also return a grounded answer (+1 credit)
            include_domains: restrict results to these domains
            exclude_domains: drop results from these domains
            days: only results from the last N days
            topic: general | news | code | science | finance

        Returns:
            Normalized dict: {"answer", "results", "quotes", "raw"}
        """
        arguments = {
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": include_answer,
            "topic": topic,
        }
        if include_domains:
            arguments["include_domains"] = include_domains
        if exclude_domains:
            arguments["exclude_domains"] = exclude_domains
        if days is not None:
            arguments["days"] = days

        result = self._rpc("tools/call", {"name": "web_search", "arguments": arguments})
        return normalize_results(_unwrap_tool_result(result))

    def extract_url(
        self,
        urls,
        query: Optional[str] = None,
        format: str = "markdown",
    ) -> Dict:
        """
        Fetch one or more URLs and return their main content, boilerplate removed.

        Args:
            urls: a single URL or a list of URLs
            query: optional focus for the extraction
            format: markdown | text
        """
        if isinstance(urls, str):
            urls = [urls]

        arguments = {"urls": urls, "format": format}
        if query:
            arguments["query"] = query

        result = self._rpc("tools/call", {"name": "extract_url", "arguments": arguments})
        return _unwrap_tool_result(result)
