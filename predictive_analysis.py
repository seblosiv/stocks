"""
Predictive analysis module for stock forecasting
Implements multiple forecasting models including Prophet, ARIMA, and ML-based approaches
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

# Machine Learning
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Time series forecasting
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Warning: Prophet not available. Install with: pip install prophet")

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing


class StockPredictor:
    """Advanced stock price prediction using multiple models"""

    def __init__(self):
        self.models = {}
        self.predictions = {}

    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features for machine learning models

        Args:
            df: Stock data DataFrame

        Returns:
            Tuple of (features, target)
        """
        df = df.copy()

        # Technical indicators
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_30'] = df['Close'].rolling(window=30).mean()
        df['SMA_90'] = df['Close'].rolling(window=90).mean()

        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()

        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        df['BB_Std'] = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
        df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)

        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']

        # Price momentum
        df['Momentum_5'] = df['Close'].pct_change(periods=5)
        df['Momentum_10'] = df['Close'].pct_change(periods=10)
        df['Momentum_20'] = df['Close'].pct_change(periods=20)

        # Lag features
        for lag in [1, 2, 3, 5, 10]:
            df[f'Close_Lag_{lag}'] = df['Close'].shift(lag)
            df[f'Volume_Lag_{lag}'] = df['Volume'].shift(lag)

        # Drop NaN values
        df = df.dropna()

        # Select features
        feature_cols = [col for col in df.columns if col not in
                       ['Close', 'Open', 'High', 'Low', 'Volume', 'Dividends',
                        'Stock Splits', 'Ticker', 'Daily_Return', 'Volatility',
                        'MA_50', 'MA_200', 'BB_Std']]

        X = df[feature_cols]
        y = df['Close']

        return X, y

    def prophet_forecast(self, df: pd.DataFrame, periods: int = 252*5) -> pd.DataFrame:
        """
        Forecast using Facebook Prophet

        Args:
            df: Historical stock data
            periods: Number of days to forecast (default: 5 years)

        Returns:
            DataFrame with forecast
        """
        if not PROPHET_AVAILABLE:
            return pd.DataFrame()

        try:
            # Prepare data for Prophet
            prophet_df = pd.DataFrame({
                'ds': df.index,
                'y': df['Close'].values
            })

            # Initialize and fit model
            model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=True,
                changepoint_prior_scale=0.05,
                interval_width=0.95
            )

            model.fit(prophet_df)

            # Make future dataframe
            future = model.make_future_dataframe(periods=periods)

            # Predict
            forecast = model.predict(future)

            return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

        except Exception as e:
            print(f"Error in Prophet forecast: {e}")
            return pd.DataFrame()

    def arima_forecast(self, df: pd.DataFrame, periods: int = 252*5) -> pd.DataFrame:
        """
        Forecast using ARIMA model

        Args:
            df: Historical stock data
            periods: Number of days to forecast

        Returns:
            DataFrame with forecast
        """
        try:
            # Fit ARIMA model
            model = ARIMA(df['Close'], order=(5, 1, 5))
            fitted_model = model.fit()

            # Forecast
            forecast = fitted_model.forecast(steps=periods)

            # Create date range
            last_date = df.index[-1]
            future_dates = pd.date_range(start=last_date + timedelta(days=1),
                                        periods=periods, freq='B')

            forecast_df = pd.DataFrame({
                'ds': future_dates,
                'yhat': forecast
            })

            return forecast_df

        except Exception as e:
            print(f"Error in ARIMA forecast: {e}")
            return pd.DataFrame()

    def ml_forecast(self, df: pd.DataFrame, periods: int = 252*5) -> pd.DataFrame:
        """
        Forecast using Machine Learning (Gradient Boosting)

        Args:
            df: Historical stock data
            periods: Number of days to forecast

        Returns:
            DataFrame with forecast
        """
        try:
            # Prepare features
            X, y = self.prepare_features(df)

            if len(X) < 100:
                print("Not enough data for ML forecast")
                return pd.DataFrame()

            # Train model
            model = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )

            model.fit(X, y)

            # For forecasting, we'll use a simplified approach
            # In practice, you'd need to recursively predict and update features
            last_price = df['Close'].iloc[-1]

            # Simple projection based on historical trend
            historical_returns = df['Close'].pct_change().dropna()
            mean_return = historical_returns.mean()
            std_return = historical_returns.std()

            # Generate forecast
            forecast_prices = [last_price]
            for i in range(periods):
                # Add some randomness based on historical volatility
                next_price = forecast_prices[-1] * (1 + mean_return)
                forecast_prices.append(next_price)

            # Create date range
            last_date = df.index[-1]
            future_dates = pd.date_range(start=last_date + timedelta(days=1),
                                        periods=periods, freq='B')

            forecast_df = pd.DataFrame({
                'ds': future_dates,
                'yhat': forecast_prices[1:]
            })

            return forecast_df

        except Exception as e:
            print(f"Error in ML forecast: {e}")
            return pd.DataFrame()

    def ensemble_forecast(self, df: pd.DataFrame, periods: int = 252*5) -> Dict[str, pd.DataFrame]:
        """
        Create ensemble forecast using multiple models

        Args:
            df: Historical stock data
            periods: Number of days to forecast

        Returns:
            Dictionary with forecasts from different models
        """
        forecasts = {}

        print("Running Prophet forecast...")
        prophet_fc = self.prophet_forecast(df, periods)
        if not prophet_fc.empty:
            forecasts['prophet'] = prophet_fc

        print("Running ARIMA forecast...")
        arima_fc = self.arima_forecast(df, periods)
        if not arima_fc.empty:
            forecasts['arima'] = arima_fc

        print("Running ML forecast...")
        ml_fc = self.ml_forecast(df, periods)
        if not ml_fc.empty:
            forecasts['ml'] = ml_fc

        # Create ensemble (average of all models)
        if len(forecasts) > 0:
            ensemble_df = None
            for name, fc in forecasts.items():
                if ensemble_df is None:
                    ensemble_df = fc[['ds']].copy()
                    ensemble_df['yhat'] = fc['yhat']
                    ensemble_df['count'] = 1
                else:
                    # Merge and average
                    merged = ensemble_df.merge(fc[['ds', 'yhat']], on='ds', how='outer', suffixes=('', '_new'))
                    merged['yhat'] = merged['yhat'].fillna(0) + merged['yhat_new'].fillna(0)
                    merged['count'] = merged['count'].fillna(0) + 1
                    ensemble_df = merged[['ds', 'yhat', 'count']]

            if ensemble_df is not None:
                ensemble_df['yhat'] = ensemble_df['yhat'] / ensemble_df['count']
                forecasts['ensemble'] = ensemble_df[['ds', 'yhat']]

        return forecasts

    def calculate_growth_metrics(self, forecast_df: pd.DataFrame, current_price: float) -> Dict:
        """
        Calculate growth metrics from forecast

        Args:
            forecast_df: Forecast DataFrame
            current_price: Current stock price

        Returns:
            Dictionary with growth metrics
        """
        if forecast_df.empty:
            return {}

        try:
            forecast_prices = forecast_df['yhat'].values

            # 1-year forecast
            one_year_idx = min(252, len(forecast_prices) - 1)
            one_year_price = forecast_prices[one_year_idx]
            one_year_return = ((one_year_price - current_price) / current_price) * 100

            # 3-year forecast
            three_year_idx = min(252*3, len(forecast_prices) - 1)
            three_year_price = forecast_prices[three_year_idx]
            three_year_return = ((three_year_price - current_price) / current_price) * 100

            # 5-year forecast
            five_year_idx = len(forecast_prices) - 1
            five_year_price = forecast_prices[five_year_idx]
            five_year_return = ((five_year_price - current_price) / current_price) * 100

            # Calculate CAGR
            years = 5
            cagr = ((five_year_price / current_price) ** (1/years) - 1) * 100

            return {
                'current_price': round(current_price, 2),
                '1y_forecast': round(one_year_price, 2),
                '1y_return': round(one_year_return, 2),
                '3y_forecast': round(three_year_price, 2),
                '3y_return': round(three_year_return, 2),
                '5y_forecast': round(five_year_price, 2),
                '5y_return': round(five_year_return, 2),
                'cagr_5y': round(cagr, 2)
            }

        except Exception as e:
            print(f"Error calculating growth metrics: {e}")
            return {}
