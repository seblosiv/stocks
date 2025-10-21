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
