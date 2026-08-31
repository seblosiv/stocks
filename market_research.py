"""
Stock research built on the Neurobird Search API

Turns the tickers tracked by the dashboard into targeted web-research queries:
recent news, catalysts and risks, and sector-level briefings.
"""

from typing import Dict, List, Optional

from config import (
    ALL_STOCKS,
    NEWS_LOOKBACK_DAYS,
    NEWS_MAX_RESULTS,
    RESEARCH_EXCLUDE_DOMAINS,
    RESEARCH_MAX_RESULTS,
    RESEARCH_SEARCH_DEPTH,
    SECTOR_TOPICS,
)
from neurobird_search import NeurobirdClient


def _company_name(ticker: str, stocks: Dict[str, str]) -> str:
    """Human-readable company name, with the config's parenthetical note dropped"""
    label = stocks.get(ticker, ticker)
    return label.split("(")[0].strip() or ticker


class StockResearcher:
    """Ticker-aware research queries against the Neurobird Search API"""

    def __init__(self, client: Optional[NeurobirdClient] = None,
                 stocks: Optional[Dict[str, str]] = None):
        self.client = client or NeurobirdClient()
        self.stocks = stocks or ALL_STOCKS

    def news(self, ticker: str, days: int = NEWS_LOOKBACK_DAYS,
             max_results: int = NEWS_MAX_RESULTS) -> Dict:
        """Recent news for a ticker, restricted to the last `days` days"""
        name = _company_name(ticker, self.stocks)
        query = (
            f"{name} ({ticker}) stock news: earnings, contracts, partnerships, "
            f"analyst ratings and guidance"
        )
        return self.client.web_search(
            query=query,
            topic="news",
            days=days,
            max_results=max_results,
            search_depth="standard",
            include_answer=True,
            exclude_domains=RESEARCH_EXCLUDE_DOMAINS,
        )

    def deep_dive(self, ticker: str,
                  max_results: int = RESEARCH_MAX_RESULTS) -> Dict:
        """Catalysts, risks and competitive position for a ticker"""
        name = _company_name(ticker, self.stocks)
        query = (
            f"{name} ({ticker}) investment thesis: growth catalysts, key risks, "
            f"competitive position, revenue outlook and analyst price targets"
        )
        return self.client.web_search(
            query=query,
            topic="finance",
            max_results=max_results,
            search_depth=RESEARCH_SEARCH_DEPTH,
            include_answer=True,
            exclude_domains=RESEARCH_EXCLUDE_DOMAINS,
        )

    def sector_briefing(self, sector: str,
                        days: int = NEWS_LOOKBACK_DAYS,
                        max_results: int = RESEARCH_MAX_RESULTS) -> Dict:
        """Sector-wide briefing for 'Nuclear Fusion' or 'Quantum Computing'"""
        topic = SECTOR_TOPICS.get(sector, sector)
        return self.client.web_search(
            query=f"Latest {topic}",
            topic="news",
            days=days,
            max_results=max_results,
            search_depth=RESEARCH_SEARCH_DEPTH,
            include_answer=True,
            exclude_domains=RESEARCH_EXCLUDE_DOMAINS,
        )

    def compare(self, tickers: List[str],
                max_results: int = RESEARCH_MAX_RESULTS) -> Dict:
        """Head-to-head research across several tickers"""
        names = ", ".join(
            f"{_company_name(t, self.stocks)} ({t})" for t in tickers
        )
        return self.client.web_search(
            query=(
                f"Compare the investment outlook for {names}: recent performance "
                f"drivers, valuation and analyst sentiment"
            ),
            topic="finance",
            max_results=max_results,
            search_depth=RESEARCH_SEARCH_DEPTH,
            include_answer=True,
            exclude_domains=RESEARCH_EXCLUDE_DOMAINS,
        )

    def ask(self, question: str, **kwargs) -> Dict:
        """Free-form research question"""
        params = {
            "topic": "finance",
            "max_results": RESEARCH_MAX_RESULTS,
            "search_depth": RESEARCH_SEARCH_DEPTH,
            "include_answer": True,
            "exclude_domains": RESEARCH_EXCLUDE_DOMAINS,
        }
        params.update(kwargs)
        return self.client.web_search(query=question, **params)

    def read_article(self, url: str, query: Optional[str] = None) -> Dict:
        """Pull the full text of a source article as markdown"""
        return self.client.extract_url(url, query=query)
