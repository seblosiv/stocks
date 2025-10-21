# Quick Start Guide

Get up and running with the Fusion & Quantum Computing Stock Dashboard in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Internet connection (for downloading stock data)

## Installation Steps

### Option 1: Using Launcher Scripts (Easiest)

**On Linux/Mac:**
```bash
./run.sh
```

**On Windows:**
```
run.bat
```

These scripts will automatically:
1. Create a virtual environment
2. Install all dependencies
3. Launch the dashboard

### Option 2: Manual Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

2. **Activate it**
   ```bash
   # Linux/Mac
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

3. **Install packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Verify Setup

Before running the dashboard, verify everything is installed correctly:

```bash
python verify_setup.py
```

This will check all dependencies and test data fetching.

## First Run

1. The app will open in your browser at `http://localhost:8501`
2. First load takes 2-3 minutes (downloading historical data for all stocks)
3. Subsequent runs are much faster (data is cached)

## Quick Tour

### Overview Page
- See all stocks at a glance
- Compare fusion vs quantum sectors
- View top performers

### Fusion Stocks
- Analyze nuclear fusion related companies
- Compare lithium, uranium, and fusion tech stocks

### Quantum Computing
- Track pure-play quantum companies
- Monitor big tech quantum divisions

### Stock Analysis
- Deep dive into individual stocks
- View technical indicators
- Analyze price movements

### Forecasting
- Generate 5-year predictions
- See ensemble model forecasts
- Understand growth potential

## Tips

- Use the sidebar to adjust time periods
- First run downloads all data (be patient!)
- Forecasts take 30-60 seconds to generate
- Click on legend items to hide/show stocks
- Hover over charts for detailed info

## Troubleshooting

**App won't start?**
- Check Python version: `python --version` (need 3.8+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

**No data showing?**
- Check internet connection
- Some stocks may have limited historical data
- Try a different time period from sidebar

**Slow performance?**
- Reduce number of stocks selected
- Use shorter time periods
- Close other browser tabs

**Forecast not working?**
- Prophet may need additional setup on Windows
- Try with different stocks
- Check verify_setup.py output

## What to Expect

### Data Update Frequency
- Historical data: Cached for 1 hour
- Stock prices: From Yahoo Finance (15-20 min delay)

### Forecast Accuracy
- Forecasts are educational only
- Based on historical patterns
- NOT financial advice
- Always do your own research

## Next Steps

1. Explore different stocks
2. Compare performance across sectors
3. Generate forecasts for promising stocks
4. Read the full README.md for advanced features
5. Customize config.py to add your favorite stocks

## Need Help?

- Check the full README.md
- Review error messages in terminal
- Run verify_setup.py to diagnose issues
- Check that all files are present

## Happy Analyzing!

Remember: This is for educational purposes only. Always consult with financial advisors before making investment decisions.

---

Ready to dive deeper? Check out [README.md](README.md) for the complete documentation.
