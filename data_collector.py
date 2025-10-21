"""
Data collection module for stock market data
Handles data fetching, caching, and preprocessing
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class StockDataCollector:
    """Collects and processes stock market data"""

    def __init__(self, stocks: Dict[str, str]):
        self.stocks = stocks
        self.data_cache = {}

    def fetch_stock_data(self, ticker: str, period: str = "5y") -> pd.DataFrame:
        """
        Fetch historical stock data for a given ticker

        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            DataFrame with stock data
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)

            if df.empty:
                print(f"Warning: No data found for {ticker}")
                return pd.DataFrame()

            # Add ticker column
            df['Ticker'] = ticker

            # Calculate additional metrics
            df['Daily_Return'] = df['Close'].pct_change()
            df['Volatility'] = df['Daily_Return'].rolling(window=30).std()
            df['MA_50'] = df['Close'].rolling(window=50).mean()
            df['MA_200'] = df['Close'].rolling(window=200).mean()

            return df

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()

    def fetch_multiple_stocks(self, tickers: List[str], period: str = "5y") -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks

        Args:
            tickers: List of ticker symbols
            period: Time period

        Returns:
            Dictionary mapping tickers to DataFrames
        """
        stock_data = {}

        for ticker in tickers:
            print(f"Fetching data for {ticker}...")
            df = self.fetch_stock_data(ticker, period)
            if not df.empty:
                stock_data[ticker] = df

        return stock_data

    def get_current_metrics(self, ticker: str) -> Dict:
        """
        Get current stock metrics and information

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with current metrics
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            metrics = {
                'ticker': ticker,
                'name': info.get('longName', 'N/A'),
                'current_price': info.get('currentPrice', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_book': info.get('priceToBook', 0),
                'dividend_yield': info.get('dividendYield', 0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                'avg_volume': info.get('averageVolume', 0),
                'beta': info.get('beta', 0),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
            }

            return metrics

        except Exception as e:
            print(f"Error fetching metrics for {ticker}: {e}")
            return {'ticker': ticker, 'error': str(e)}

    def calculate_performance_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate performance metrics from stock data

        Args:
            df: DataFrame with stock data

        Returns:
            Dictionary with performance metrics
        """
        if df.empty or len(df) < 2:
            return {}

        try:
            # Calculate returns
            total_return = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100

            # Calculate annualized metrics
            years = len(df) / 252  # Trading days in a year
            annualized_return = ((1 + total_return/100) ** (1/years) - 1) * 100

            # Calculate volatility
            daily_returns = df['Daily_Return'].dropna()
            volatility = daily_returns.std() * np.sqrt(252) * 100  # Annualized

            # Calculate Sharpe ratio (assuming 4% risk-free rate)
            risk_free_rate = 4.0
            sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0

            # Calculate max drawdown
            cumulative = (1 + daily_returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100

            return {
                'total_return': round(total_return, 2),
                'annualized_return': round(annualized_return, 2),
                'volatility': round(volatility, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_drawdown, 2),
                'current_price': round(df['Close'].iloc[-1], 2),
                'start_price': round(df['Close'].iloc[0], 2),
            }

        except Exception as e:
            print(f"Error calculating performance metrics: {e}")
            return {}

    def get_portfolio_summary(self, stock_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Create a summary DataFrame of all stocks in portfolio

        Args:
            stock_data: Dictionary mapping tickers to DataFrames

        Returns:
            Summary DataFrame
        """
        summary_data = []

        for ticker, df in stock_data.items():
            if not df.empty:
                metrics = self.calculate_performance_metrics(df)
                metrics['ticker'] = ticker
                metrics['name'] = self.stocks.get(ticker, ticker)
                summary_data.append(metrics)

        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            # Reorder columns
            cols = ['ticker', 'name', 'current_price', 'total_return', 'annualized_return',
                    'volatility', 'sharpe_ratio', 'max_drawdown']
            summary_df = summary_df[[col for col in cols if col in summary_df.columns]]
            return summary_df.sort_values('total_return', ascending=False)

        return pd.DataFrame()
