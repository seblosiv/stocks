"""
Configuration file for Fusion & Quantum Computing Stock Dashboard
Contains curated lists of top stocks in nuclear fusion and quantum computing sectors
"""

# Nuclear Fusion Stocks
FUSION_STOCKS = {
    # Pure-play and major fusion companies
    "LTHM": "Livent Corporation (Lithium supplier)",
    "ALB": "Albemarle Corporation (Lithium)",
    "BWXT": "BWX Technologies (Nuclear tech)",
    "CCJ": "Cameco Corporation (Uranium)",
    "UEC": "Uranium Energy Corp",
    "UUUU": "Energy Fuels Inc (Uranium)",
    "DNN": "Denison Mines (Uranium)",
    "LEU": "Centrus Energy Corp (Nuclear fuel)",
    "GE": "General Electric (Fusion research)",
    "LMT": "Lockheed Martin (Fusion research)",
    # Note: Many fusion companies are private (Commonwealth Fusion, TAE, Helion)
}

# Quantum Computing Stocks
QUANTUM_STOCKS = {
    # Pure-play quantum companies
    "IONQ": "IonQ Inc (Trapped ion quantum)",
    "RGTI": "Rigetti Computing (Superconducting quantum)",
    "QUBT": "Quantum Computing Inc",

    # Major tech companies with quantum divisions
    "IBM": "IBM (Quantum computing leader)",
    "GOOGL": "Alphabet/Google (Quantum AI)",
    "MSFT": "Microsoft (Azure Quantum)",
    "AMZN": "Amazon (AWS Quantum)",
    "INTC": "Intel (Quantum hardware)",
    "NVDA": "NVIDIA (Quantum simulation)",

    # Quantum-adjacent companies
    "FORM": "FormFactor (Quantum testing)",
    "ATOM": "Atomera (Advanced materials)",
}

# Combined portfolio
ALL_STOCKS = {**FUSION_STOCKS, **QUANTUM_STOCKS}

# Market indices for comparison
BENCHMARK_INDICES = {
    "^GSPC": "S&P 500",
    "^IXIC": "NASDAQ Composite",
    "^DJI": "Dow Jones Industrial Average"
}

# Analysis parameters
HISTORICAL_YEARS = 5
FORECAST_YEARS = 5
CONFIDENCE_INTERVAL = 0.95

# Dashboard configuration
THEME_COLOR = "#1E88E5"
APP_TITLE = "Fusion & Quantum Computing Stock Dashboard"
APP_ICON = "⚛️"

# --- Neurobird Search API -------------------------------------------------
# Live web search / news research for the tracked tickers.
# Set NEUROBIRD_KEY in your environment or in .streamlit/secrets.toml.
# A free key (1,000 credits/month) can be provisioned with:
#   python -c "import neurobird_search as n; print(n.create_api_key())"

NEUROBIRD_BASE_URL = "https://search.neurobird.com"

# Default search parameters (see neurobird_search.NeurobirdClient.web_search)
NEWS_LOOKBACK_DAYS = 14        # only surface news from the last N days
NEWS_MAX_RESULTS = 6           # results per news query
RESEARCH_MAX_RESULTS = 8       # results per deep-dive query
RESEARCH_SEARCH_DEPTH = "advanced"  # basic | standard | advanced

# Cache research responses for this long to conserve API credits
RESEARCH_CACHE_TTL = 900       # seconds

# Domains that tend to carry low-signal, SEO-farmed stock content
RESEARCH_EXCLUDE_DOMAINS = [
    "stocktwits.com",
    "investorshub.advfn.com",
]

# Sector-level research topics
SECTOR_TOPICS = {
    "Nuclear Fusion": (
        "nuclear fusion energy industry commercial reactor milestones, "
        "funding rounds and public company developments"
    ),
    "Quantum Computing": (
        "quantum computing industry qubit milestones, error correction "
        "breakthroughs, enterprise contracts and public company developments"
    ),
}
