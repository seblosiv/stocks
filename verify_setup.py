"""
Setup verification script
Checks if all required dependencies are installed and working
"""

import sys


def check_imports():
    """Check if all required packages can be imported"""
    print("Checking package imports...\n")

    packages = [
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('streamlit', 'Streamlit'),
        ('plotly', 'Plotly'),
        ('yfinance', 'yfinance'),
        ('sklearn', 'scikit-learn'),
        ('statsmodels', 'statsmodels'),
    ]

    optional_packages = [
        ('prophet', 'Prophet'),
        ('talib', 'TA-Lib'),
    ]

    failed = []
    optional_failed = []

    # Check required packages
    for module, name in packages:
        try:
            __import__(module)
            print(f"✓ {name:20s} - OK")
        except ImportError as e:
            print(f"✗ {name:20s} - FAILED: {e}")
            failed.append(name)

    # Check optional packages
    print("\nOptional packages:")
    for module, name in optional_packages:
        try:
            __import__(module)
            print(f"✓ {name:20s} - OK")
        except ImportError as e:
            print(f"⚠ {name:20s} - Not installed (optional)")
            optional_failed.append(name)

    print("\n" + "="*60)

    if failed:
        print(f"\n❌ Setup FAILED - Missing {len(failed)} required package(s):")
        for pkg in failed:
            print(f"   - {pkg}")
        print("\nPlease install missing packages:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All required packages are installed!")

        if optional_failed:
            print(f"\n⚠️  {len(optional_failed)} optional package(s) not installed:")
            for pkg in optional_failed:
                print(f"   - {pkg}")
            print("\nThe app will work, but some features may be limited.")

        return True


def test_data_fetch():
    """Test if we can fetch stock data"""
    print("\n" + "="*60)
    print("Testing stock data fetch...\n")

    try:
        import yfinance as yf

        print("Fetching test data for AAPL...")
        stock = yf.Ticker("AAPL")
        df = stock.history(period="1mo")

        if df.empty:
            print("✗ Failed to fetch data")
            return False

        print(f"✓ Successfully fetched {len(df)} days of data")
        print(f"  Latest close: ${df['Close'].iloc[-1]:.2f}")
        return True

    except Exception as e:
        print(f"✗ Error fetching data: {e}")
        return False


def test_modules():
    """Test custom modules"""
    print("\n" + "="*60)
    print("Testing custom modules...\n")

    try:
        from config import ALL_STOCKS, FUSION_STOCKS, QUANTUM_STOCKS
        print(f"✓ config.py loaded successfully")
        print(f"  Total stocks: {len(ALL_STOCKS)}")
        print(f"  Fusion stocks: {len(FUSION_STOCKS)}")
        print(f"  Quantum stocks: {len(QUANTUM_STOCKS)}")

        from data_collector import StockDataCollector
        print("✓ data_collector.py loaded successfully")

        from predictive_analysis import StockPredictor
        print("✓ predictive_analysis.py loaded successfully")

        return True

    except Exception as e:
        print(f"✗ Error loading modules: {e}")
        return False


def main():
    """Main verification function"""
    print("="*60)
    print("Fusion & Quantum Stock Dashboard - Setup Verification")
    print("="*60)
    print(f"\nPython version: {sys.version}")
    print()

    # Run checks
    imports_ok = check_imports()
    modules_ok = test_modules()
    data_ok = test_data_fetch()

    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)

    print(f"\nPackage imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Custom modules:  {'✅ PASS' if modules_ok else '❌ FAIL'}")
    print(f"Data fetching:   {'✅ PASS' if data_ok else '❌ FAIL'}")

    if imports_ok and modules_ok and data_ok:
        print("\n" + "🎉 "*10)
        print("Setup verification PASSED!")
        print("You can now run the dashboard with:")
        print("  streamlit run app.py")
        print("\nOr use the launcher scripts:")
        print("  ./run.sh (Linux/Mac)")
        print("  run.bat (Windows)")
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
