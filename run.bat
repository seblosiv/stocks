@echo off

echo ==================================
echo Fusion ^& Quantum Stock Dashboard
echo ==================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist "venv\installed" (
    echo Installing requirements...
    pip install -r requirements.txt
    type nul > venv\installed
    echo Requirements installed.
) else (
    echo Requirements already installed.
)

echo.
echo Starting dashboard...
echo The dashboard will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run Streamlit
streamlit run app.py

pause
