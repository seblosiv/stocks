"""
Fusion & Quantum Computing Stock Dashboard
A high-end dashboard for analyzing and forecasting stocks in the fusion and quantum computing sectors
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import custom modules
from config import (
    FUSION_STOCKS, QUANTUM_STOCKS, ALL_STOCKS,
    BENCHMARK_INDICES, APP_TITLE, APP_ICON,
    FORECAST_YEARS, RESEARCH_CACHE_TTL, NEWS_LOOKBACK_DAYS
)
from data_collector import StockDataCollector
from predictive_analysis import StockPredictor
from market_research import StockResearcher
from neurobird_search import NeurobirdClient, NeurobirdError, get_api_key

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
    }
    h1 {
        color: #667eea;
        font-weight: 700;
    }
    h2 {
        color: #764ba2;
        font-weight: 600;
    }
    .highlight {
        background-color: #667eea;
        padding: 2px 8px;
        border-radius: 4px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_stock_data(tickers, period="5y"):
    """Load stock data with caching"""
    collector = StockDataCollector(ALL_STOCKS)
    return collector.fetch_multiple_stocks(tickers, period)


def resolve_neurobird_key():
    """Neurobird API key from Streamlit secrets, falling back to the environment"""
    try:
        key = st.secrets.get("NEUROBIRD_KEY")
        if key:
            return key
    except Exception:
        # No secrets.toml configured - fall through to the environment
        pass
    return get_api_key()


def get_researcher():
    """Build a StockResearcher, or None when no API key is configured"""
    key = resolve_neurobird_key()
    if not key:
        return None
    return StockResearcher(client=NeurobirdClient(api_key=key))


@st.cache_data(ttl=RESEARCH_CACHE_TTL, show_spinner=False)
def run_research(kind, target, api_key):
    """
    Cached research call. `api_key` is part of the cache key so switching keys
    re-runs the query; caching keeps repeated page views from burning credits.
    """
    researcher = StockResearcher(client=NeurobirdClient(api_key=api_key))
    if kind == "news":
        return researcher.news(target)
    if kind == "deep_dive":
        return researcher.deep_dive(target)
    if kind == "sector":
        return researcher.sector_briefing(target)
    if kind == "ask":
        return researcher.ask(target)
    raise ValueError(f"Unknown research kind: {kind}")


def render_research(payload):
    """Render a normalized Neurobird search payload"""
    answer = payload.get("answer")
    results = payload.get("results", [])

    if answer:
        st.markdown("#### Summary")
        st.info(answer)

    if not results:
        if not answer:
            st.warning("No results returned for this query.")
        return

    st.markdown("#### Sources")
    for item in results:
        title = item.get("title") or "Untitled"
        url = item.get("url") or ""
        published = item.get("published")

        header = f"**[{title}]({url})**" if url else f"**{title}**"
        if published:
            header += f"  \n*{published}*"
        st.markdown(header)

        content = (item.get("content") or "").strip()
        if content:
            excerpt = content if len(content) <= 1200 else content[:1200] + "..."
            with st.expander("Show extracted passage"):
                st.markdown(excerpt)
        st.markdown("---")


def research_section(kind, target, label, key_suffix=""):
    """Button-gated research block so searches only run on demand"""
    api_key = resolve_neurobird_key()

    if not api_key:
        st.info(
            "Live research is powered by the Neurobird Search API. Set "
            "`NEUROBIRD_KEY` in your environment or in `.streamlit/secrets.toml` "
            "to enable it. A free key (1,000 credits/month) is available - see "
            "the README."
        )
        return

    if st.button(label, key=f"research_{kind}_{target}{key_suffix}"):
        with st.spinner("Searching the live web..."):
            try:
                payload = run_research(kind, target, api_key)
            except NeurobirdError as exc:
                st.error(f"Neurobird search failed: {exc}")
                return
        render_research(payload)


@st.cache_data(ttl=3600)
def get_stock_summary(stock_data):
    """Get portfolio summary with caching"""
    collector = StockDataCollector(ALL_STOCKS)
    return collector.get_portfolio_summary(stock_data)


def plot_stock_performance(stock_data, selected_stocks):
    """Plot stock performance comparison"""
    fig = go.Figure()

    for ticker in selected_stocks:
        if ticker in stock_data and not stock_data[ticker].empty:
            df = stock_data[ticker]
            # Normalize to 100 for comparison
            normalized = (df['Close'] / df['Close'].iloc[0]) * 100

            fig.add_trace(go.Scatter(
                x=df.index,
                y=normalized,
                name=ticker,
                mode='lines',
                line=dict(width=2),
                hovertemplate='%{y:.2f}<extra></extra>'
            ))

    fig.update_layout(
        title="Stock Performance Comparison (Normalized to 100)",
        xaxis_title="Date",
        yaxis_title="Normalized Price",
        hovermode='x unified',
        template='plotly_dark',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def plot_forecast(historical_df, forecast_df, ticker):
    """Plot historical data and forecast"""
    fig = go.Figure()

    # Historical data
    fig.add_trace(go.Scatter(
        x=historical_df.index,
        y=historical_df['Close'],
        name='Historical',
        line=dict(color='#667eea', width=2),
        mode='lines'
    ))

    # Forecast
    if not forecast_df.empty and 'ds' in forecast_df.columns:
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat'],
            name='Forecast',
            line=dict(color='#f093fb', width=2, dash='dash'),
            mode='lines'
        ))

        # Confidence interval if available
        if 'yhat_lower' in forecast_df.columns and 'yhat_upper' in forecast_df.columns:
            fig.add_trace(go.Scatter(
                x=forecast_df['ds'],
                y=forecast_df['yhat_upper'],
                fill=None,
                mode='lines',
                line_color='rgba(240, 147, 251, 0)',
                showlegend=False,
                name='Upper Bound'
            ))

            fig.add_trace(go.Scatter(
                x=forecast_df['ds'],
                y=forecast_df['yhat_lower'],
                fill='tonexty',
                mode='lines',
                line_color='rgba(240, 147, 251, 0)',
                name='95% Confidence',
                fillcolor='rgba(240, 147, 251, 0.2)'
            ))

    fig.update_layout(
        title=f"{ticker} - Historical Data & 5-Year Forecast",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        hovermode='x unified',
        template='plotly_dark',
        height=600
    )

    return fig


def plot_technical_indicators(df, ticker):
    """Plot technical indicators"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{ticker} Price & Moving Averages', 'Volume', 'RSI'),
        row_heights=[0.5, 0.25, 0.25]
    )

    # Price and Moving Averages
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ), row=1, col=1)

    if 'MA_50' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA_50'],
            name='MA 50',
            line=dict(color='orange', width=1)
        ), row=1, col=1)

    if 'MA_200' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA_200'],
            name='MA 200',
            line=dict(color='red', width=1)
        ), row=1, col=1)

    # Volume
    colors = ['red' if row['Close'] < row['Open'] else 'green'
              for _, row in df.iterrows()]

    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name='Volume',
        marker_color=colors
    ), row=2, col=1)

    # RSI
    if 'Daily_Return' in df.columns:
        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=rsi,
            name='RSI',
            line=dict(color='purple', width=2)
        ), row=3, col=1)

        # Add RSI reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                     opacity=0.5, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green",
                     opacity=0.5, row=3, col=1)

    fig.update_layout(
        template='plotly_dark',
        height=900,
        showlegend=True,
        xaxis_rangeslider_visible=False
    )

    return fig


def plot_sector_comparison(summary_df, sector_type):
    """Plot sector comparison"""
    if summary_df.empty:
        return None

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=summary_df['ticker'],
        y=summary_df['total_return'],
        text=summary_df['total_return'].round(2),
        textposition='auto',
        marker=dict(
            color=summary_df['total_return'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Return %")
        ),
        name='Total Return'
    ))

    fig.update_layout(
        title=f"{sector_type} Stocks - Total Return Comparison",
        xaxis_title="Ticker",
        yaxis_title="Total Return (%)",
        template='plotly_dark',
        height=500
    )

    return fig


def main():
    """Main application"""

    # Header
    st.markdown(f"# {APP_ICON} {APP_TITLE}")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.markdown("## Navigation")

        page = st.radio(
            "Select Page:",
            ["Overview", "Fusion Stocks", "Quantum Computing", "Stock Analysis",
             "Forecasting", "Market Research"]
        )

        st.markdown("---")
        st.markdown("## Settings")

        time_period = st.selectbox(
            "Historical Data Period:",
            ["1y", "2y", "5y", "10y", "max"],
            index=2
        )

        st.markdown("---")
        st.markdown("### Live Research")
        if resolve_neurobird_key():
            st.success("Neurobird Search API connected")
        else:
            st.caption("Set NEUROBIRD_KEY to enable live web research.")

        st.markdown("---")
        st.markdown("### About")
        st.info(
            "This dashboard analyzes stocks in the nuclear fusion and "
            "quantum computing sectors, providing historical analysis and "
            "5-year forecasts using advanced ML models."
        )

    # Load data
    with st.spinner("Loading stock data..."):
        stock_data = load_stock_data(list(ALL_STOCKS.keys()), time_period)
        summary_df = get_stock_summary(stock_data)

    # Overview Page
    if page == "Overview":
        st.markdown("## Portfolio Overview")

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        if not summary_df.empty:
            with col1:
                st.metric(
                    "Total Stocks Tracked",
                    len(summary_df),
                    delta=None
                )

            with col2:
                avg_return = summary_df['total_return'].mean()
                st.metric(
                    "Average Return",
                    f"{avg_return:.2f}%",
                    delta=f"{avg_return:.2f}%"
                )

            with col3:
                top_performer = summary_df.iloc[0]
                st.metric(
                    "Top Performer",
                    top_performer['ticker'],
                    delta=f"{top_performer['total_return']:.2f}%"
                )

            with col4:
                avg_sharpe = summary_df['sharpe_ratio'].mean()
                st.metric(
                    "Avg Sharpe Ratio",
                    f"{avg_sharpe:.2f}",
                    delta=None
                )

        st.markdown("---")

        # Summary table
        st.markdown("### Stock Performance Summary")
        if not summary_df.empty:
            # Format the dataframe
            display_df = summary_df.copy()
            display_df['total_return'] = display_df['total_return'].apply(lambda x: f"{x:.2f}%")
            display_df['annualized_return'] = display_df['annualized_return'].apply(lambda x: f"{x:.2f}%")
            display_df['volatility'] = display_df['volatility'].apply(lambda x: f"{x:.2f}%")
            display_df['sharpe_ratio'] = display_df['sharpe_ratio'].apply(lambda x: f"{x:.2f}")
            display_df['max_drawdown'] = display_df['max_drawdown'].apply(lambda x: f"{x:.2f}%")

            st.dataframe(display_df, use_container_width=True, height=400)

        # Sector comparison
        col1, col2 = st.columns(2)

        with col1:
            fusion_df = summary_df[summary_df['ticker'].isin(FUSION_STOCKS.keys())]
            if not fusion_df.empty:
                fig = plot_sector_comparison(fusion_df, "Nuclear Fusion")
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            quantum_df = summary_df[summary_df['ticker'].isin(QUANTUM_STOCKS.keys())]
            if not quantum_df.empty:
                fig = plot_sector_comparison(quantum_df, "Quantum Computing")
                st.plotly_chart(fig, use_container_width=True)

    # Fusion Stocks Page
    elif page == "Fusion Stocks":
        st.markdown("## Nuclear Fusion Stocks Analysis")

        st.markdown("""
        Nuclear fusion represents the next frontier in clean energy. These companies
        are positioned to benefit from fusion breakthroughs and the supporting infrastructure.
        """)

        fusion_tickers = list(FUSION_STOCKS.keys())
        selected = st.multiselect(
            "Select stocks to compare:",
            fusion_tickers,
            default=fusion_tickers[:5]
        )

        if selected:
            fig = plot_stock_performance(stock_data, selected)
            st.plotly_chart(fig, use_container_width=True)

            # Detailed metrics
            fusion_summary = summary_df[summary_df['ticker'].isin(FUSION_STOCKS.keys())]
            if not fusion_summary.empty:
                st.markdown("### Detailed Metrics")
                st.dataframe(fusion_summary, use_container_width=True)

    # Quantum Computing Page
    elif page == "Quantum Computing":
        st.markdown("## Quantum Computing Stocks Analysis")

        st.markdown("""
        Quantum computing is revolutionizing computation. These companies are leading
        the development of quantum hardware, software, and applications.
        """)

        quantum_tickers = list(QUANTUM_STOCKS.keys())
        selected = st.multiselect(
            "Select stocks to compare:",
            quantum_tickers,
            default=quantum_tickers[:5]
        )

        if selected:
            fig = plot_stock_performance(stock_data, selected)
            st.plotly_chart(fig, use_container_width=True)

            # Detailed metrics
            quantum_summary = summary_df[summary_df['ticker'].isin(QUANTUM_STOCKS.keys())]
            if not quantum_summary.empty:
                st.markdown("### Detailed Metrics")
                st.dataframe(quantum_summary, use_container_width=True)

    # Stock Analysis Page
    elif page == "Stock Analysis":
        st.markdown("## Individual Stock Analysis")

        selected_ticker = st.selectbox(
            "Select a stock for detailed analysis:",
            list(ALL_STOCKS.keys())
        )

        if selected_ticker and selected_ticker in stock_data:
            df = stock_data[selected_ticker]
            stock_name = ALL_STOCKS[selected_ticker]

            st.markdown(f"### {selected_ticker} - {stock_name}")

            # Current metrics
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
                price_change = current_price - prev_price
                price_change_pct = (price_change / prev_price) * 100

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Current Price",
                        f"${current_price:.2f}",
                        delta=f"{price_change_pct:.2f}%"
                    )

                with col2:
                    high_52w = df['High'].tail(252).max()
                    st.metric("52W High", f"${high_52w:.2f}")

                with col3:
                    low_52w = df['Low'].tail(252).min()
                    st.metric("52W Low", f"${low_52w:.2f}")

                with col4:
                    avg_vol = df['Volume'].tail(30).mean()
                    st.metric("Avg Volume (30d)", f"{avg_vol/1e6:.2f}M")

                # Technical indicators
                st.markdown("### Technical Analysis")
                fig = plot_technical_indicators(df, selected_ticker)
                st.plotly_chart(fig, use_container_width=True)

                # Live news from the Neurobird Search API
                st.markdown("---")
                st.markdown(
                    f"### Latest News (last {NEWS_LOOKBACK_DAYS} days)"
                )
                research_section(
                    "news",
                    selected_ticker,
                    f"Fetch news for {selected_ticker}",
                )

    # Forecasting Page
    elif page == "Forecasting":
        st.markdown("## 5-Year Stock Forecast")

        st.markdown("""
        Advanced forecasting using ensemble models (Prophet, ARIMA, ML).
        **Note:** Predictions are for informational purposes only and should not be
        considered as financial advice.
        """)

        selected_ticker = st.selectbox(
            "Select a stock to forecast:",
            list(ALL_STOCKS.keys())
        )

        if st.button("Generate Forecast", type="primary"):
            if selected_ticker and selected_ticker in stock_data:
                df = stock_data[selected_ticker]

                with st.spinner(f"Generating 5-year forecast for {selected_ticker}..."):
                    predictor = StockPredictor()

                    # Generate forecast
                    forecasts = predictor.ensemble_forecast(df, periods=252 * FORECAST_YEARS)

                    if 'ensemble' in forecasts:
                        forecast_df = forecasts['ensemble']

                        # Plot
                        fig = plot_forecast(df, forecast_df, selected_ticker)
                        st.plotly_chart(fig, use_container_width=True)

                        # Calculate growth metrics
                        current_price = df['Close'].iloc[-1]
                        metrics = predictor.calculate_growth_metrics(forecast_df, current_price)

                        if metrics:
                            st.markdown("### Forecast Summary")

                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                st.metric(
                                    "Current Price",
                                    f"${metrics['current_price']:.2f}"
                                )

                            with col2:
                                st.metric(
                                    "1-Year Forecast",
                                    f"${metrics['1y_forecast']:.2f}",
                                    delta=f"{metrics['1y_return']:.2f}%"
                                )

                            with col3:
                                st.metric(
                                    "3-Year Forecast",
                                    f"${metrics['3y_forecast']:.2f}",
                                    delta=f"{metrics['3y_return']:.2f}%"
                                )

                            with col4:
                                st.metric(
                                    "5-Year Forecast",
                                    f"${metrics['5y_forecast']:.2f}",
                                    delta=f"{metrics['5y_return']:.2f}%"
                                )

                            # CAGR
                            st.markdown("---")
                            st.metric(
                                "5-Year CAGR (Compound Annual Growth Rate)",
                                f"{metrics['cagr_5y']:.2f}%"
                            )

                            # Model breakdown
                            st.markdown("### Model Comparison")

                            model_data = []
                            for model_name, fc_df in forecasts.items():
                                if model_name != 'ensemble' and not fc_df.empty:
                                    five_year_price = fc_df['yhat'].iloc[-1]
                                    five_year_return = ((five_year_price - current_price) / current_price) * 100

                                    model_data.append({
                                        'Model': model_name.upper(),
                                        '5-Year Forecast': f"${five_year_price:.2f}",
                                        '5-Year Return': f"{five_year_return:.2f}%"
                                    })

                            if model_data:
                                st.table(pd.DataFrame(model_data))

                    else:
                        st.warning("Unable to generate forecast. Please try another stock.")

    # Market Research Page
    elif page == "Market Research":
        st.markdown("## Live Market Research")
        st.markdown(
            "Web research powered by the [Neurobird Search API]"
            "(https://search.neurobird.com), which returns ranked results with "
            "the relevant page passages already extracted."
        )

        if not resolve_neurobird_key():
            st.warning(
                "No Neurobird API key configured. Set `NEUROBIRD_KEY` in your "
                "environment or in `.streamlit/secrets.toml` to enable this page."
            )
            st.code(
                'python -c "import neurobird_search as n; '
                'print(n.create_api_key())"',
                language="bash",
            )
        else:
            tab1, tab2, tab3 = st.tabs(
                ["Sector Briefings", "Company Deep Dive", "Ask Anything"]
            )

            with tab1:
                sector = st.selectbox(
                    "Sector:",
                    ["Nuclear Fusion", "Quantum Computing"],
                )
                research_section(
                    "sector", sector, f"Brief me on {sector}"
                )

            with tab2:
                ticker = st.selectbox(
                    "Company:",
                    list(ALL_STOCKS.keys()),
                    key="research_ticker",
                )
                st.caption(ALL_STOCKS.get(ticker, ""))
                research_section(
                    "deep_dive", ticker, f"Research {ticker}", key_suffix="_dd"
                )

            with tab3:
                question = st.text_input(
                    "Research question:",
                    placeholder=(
                        "e.g. Which fusion companies signed grid-scale power "
                        "agreements this year?"
                    ),
                )
                if question:
                    research_section("ask", question, "Search")

            st.markdown("---")
            st.caption(
                "Each search costs credits (1 for a standard search, 2 for an "
                "advanced one, +1 when a grounded answer is included). Results "
                f"are cached for {RESEARCH_CACHE_TTL // 60} minutes."
            )

    # Footer
    st.markdown("---")
    st.markdown(
        f"*Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}* | "
        "*Disclaimer: This is for educational purposes only. Not financial advice.*"
    )


if __name__ == "__main__":
    main()
