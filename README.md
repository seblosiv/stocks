# Fusion & Quantum Computing Stock Dashboard

A high-end Python application for analyzing and forecasting stocks in the nuclear fusion and quantum computing sectors, featuring advanced machine learning models and interactive visualizations.

## Features

- **Multi-Sector Analysis**: Track stocks in both nuclear fusion and quantum computing sectors
- **Advanced Forecasting**: 5-year stock predictions using ensemble models (Prophet, ARIMA, ML)
- **Interactive Dashboard**: Modern Streamlit-based UI with real-time data
- **Technical Analysis**: Comprehensive technical indicators (RSI, MACD, Bollinger Bands, etc.)
- **Performance Metrics**: Sharpe ratio, volatility, max drawdown, and more
- **Beautiful Visualizations**: Interactive Plotly charts with dark theme

## Tech Stack

### Core Libraries
- **Streamlit**: Modern dashboard framework
- **Plotly**: Interactive visualizations
- **Pandas & NumPy**: Data manipulation and analysis

### Financial Data
- **yfinance**: Real-time and historical stock data
- **pandas-datareader**: Additional financial data sources

### Machine Learning & Forecasting
- **Prophet**: Time series forecasting (Facebook)
- **scikit-learn**: Machine learning models
- **statsmodels**: Statistical models (ARIMA)
- **TensorFlow/Keras**: Deep learning capabilities
- **XGBoost**: Gradient boosting

### Technical Analysis
- **TA-Lib**: Technical analysis indicators
- **ta**: Python technical analysis library

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stocks
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install TA-Lib** (optional but recommended)

   TA-Lib requires additional system dependencies:

   **On macOS:**
   ```bash
   brew install ta-lib
   pip install TA-Lib
   ```

   **On Ubuntu/Debian:**
   ```bash
   sudo apt-get install build-essential wget
   wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
   tar -xzf ta-lib-0.4.0-src.tar.gz
   cd ta-lib/
   ./configure --prefix=/usr
   make
   sudo make install
   pip install TA-Lib
   ```

   **On Windows:**
   Download the appropriate wheel file from [here](https://github.com/cgohlke/talib-build/releases)

## Usage

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

### Dashboard Pages

1. **Overview**: Portfolio summary with key metrics and sector comparisons
2. **Fusion Stocks**: Analysis of nuclear fusion sector stocks
3. **Quantum Computing**: Analysis of quantum computing sector stocks
4. **Stock Analysis**: Detailed technical analysis for individual stocks
5. **Forecasting**: 5-year predictions using ensemble ML models

## Stock Coverage

### Nuclear Fusion Stocks
- **LTHM**: Livent Corporation (Lithium supplier)
- **ALB**: Albemarle Corporation (Lithium)
- **BWXT**: BWX Technologies (Nuclear tech)
- **CCJ**: Cameco Corporation (Uranium)
- **UEC**: Uranium Energy Corp
- **UUUU**: Energy Fuels Inc (Uranium)
- **DNN**: Denison Mines (Uranium)
- **LEU**: Centrus Energy Corp (Nuclear fuel)
- **GE**: General Electric (Fusion research)
- **LMT**: Lockheed Martin (Fusion research)

### Quantum Computing Stocks
- **IONQ**: IonQ Inc (Pure-play quantum)
- **RGTI**: Rigetti Computing (Pure-play quantum)
- **QUBT**: Quantum Computing Inc
- **IBM**: IBM (Quantum computing leader)
- **GOOGL**: Alphabet/Google (Quantum AI)
- **MSFT**: Microsoft (Azure Quantum)
- **AMZN**: Amazon (AWS Quantum)
- **INTC**: Intel (Quantum hardware)
- **NVDA**: NVIDIA (Quantum simulation)
- **FORM**: FormFactor (Quantum testing)
- **ATOM**: Atomera (Advanced materials)

## Project Structure

```
stocks/
├── app.py                    # Main Streamlit dashboard
├── config.py                 # Configuration and stock lists
├── data_collector.py         # Stock data fetching and processing
├── predictive_analysis.py    # ML forecasting models
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Key Features Explained

### Data Collection
- Real-time stock data from Yahoo Finance
- Historical data up to 10 years
- Automatic caching for performance
- Error handling and retry logic

### Technical Indicators
- Moving Averages (SMA, EMA)
- MACD (Moving Average Convergence Divergence)
- RSI (Relative Strength Index)
- Bollinger Bands
- Volume analysis
- Price momentum indicators

### Predictive Models

1. **Prophet**: Facebook's time series forecasting algorithm
   - Handles seasonality and trends
   - Provides confidence intervals
   - Robust to missing data

2. **ARIMA**: Statistical time series model
   - Auto-regressive integrated moving average
   - Good for short to medium-term forecasts

3. **Machine Learning**: Gradient Boosting Regressor
   - Uses multiple technical indicators as features
   - Captures non-linear patterns
   - Feature engineering for enhanced predictions

4. **Ensemble**: Combines all models
   - Averages predictions from all models
   - Reduces individual model bias
   - More robust forecasts

### Performance Metrics

- **Total Return**: Overall price change percentage
- **Annualized Return**: Average yearly return
- **Volatility**: Standard deviation of returns
- **Sharpe Ratio**: Risk-adjusted return metric
- **Max Drawdown**: Largest peak-to-trough decline
- **CAGR**: Compound Annual Growth Rate

## Configuration

Edit `config.py` to:
- Add/remove stock tickers
- Modify forecast parameters
- Adjust analysis timeframes
- Customize dashboard appearance

## Troubleshooting

### Common Issues

1. **TA-Lib installation fails**
   - The app will work without TA-Lib, some advanced indicators may be unavailable
   - Follow platform-specific installation instructions above

2. **Data not loading**
   - Check internet connection
   - Verify stock tickers are valid
   - Some stocks may have limited historical data

3. **Slow performance**
   - First run downloads all historical data (can take 2-3 minutes)
   - Subsequent runs use cached data (much faster)
   - Reduce the number of stocks or time period in sidebar

4. **Prophet not working**
   - Install cmdstanpy: `pip install cmdstanpy`
   - Prophet has platform-specific requirements

## Disclaimer

**IMPORTANT**: This application is for educational and informational purposes only. The forecasts and analysis provided should NOT be considered as financial advice. Always conduct your own research and consult with qualified financial advisors before making investment decisions.

Past performance does not guarantee future results. Stock markets are inherently risky and unpredictable.

## Future Enhancements

- [ ] Real-time streaming data
- [ ] Portfolio optimization algorithms
- [ ] Sentiment analysis from news/social media
- [ ] Options analysis
- [ ] Backtesting framework
- [ ] Export reports to PDF
- [ ] Email alerts for price targets
- [ ] Deep learning models (LSTM, Transformers)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Acknowledgments

- **yfinance**: For providing free stock data
- **Streamlit**: For the amazing dashboard framework
- **Prophet**: For the powerful forecasting algorithm
- **Plotly**: For beautiful interactive charts

---

Built with by Claude Code
