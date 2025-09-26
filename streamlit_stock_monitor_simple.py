from bollinger import add_bollinger_bands, detect_bband_big_moves

import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import time

# Configure page
st.set_page_config(
    page_title="Real-Time Stock Monitor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 Real-Time Stock Monitor with Moving Averages")
st.markdown("**Live monitoring of stock prices with 9-day and 20-day moving averages**")

# Sidebar for controls
st.sidebar.header("🎛️ Controls")

# Stock ticker input
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL", max_chars=10).upper()

# Time period selection
period_options = {
    "1 Day": "1d",
    "5 Days": "5d", 
    "1 Month": "1mo",
    "3 Months": "3mo"
}
selected_period = st.sidebar.selectbox("Data Period", options=list(period_options.keys()), index=0)
period = period_options[selected_period]

# Interval selection
interval_options = {
    "1 Minute": "1m",
    "2 Minutes": "2m",
    "5 Minutes": "5m",
    "15 Minutes": "15m",
    "1 Hour": "1h"
}
selected_interval = st.sidebar.selectbox("Data Interval", options=list(interval_options.keys()), index=0)
interval = interval_options[selected_interval]

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("Auto Refresh (30 seconds)", value=True)

# Manual refresh button
if st.sidebar.button("🔄 Refresh Now"):
    st.rerun()

@st.cache_data(ttl=30)  # Cache for 30 seconds
def fetch_stock_data(ticker, period, interval):
    """Fetch stock data with caching"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)

        if data.empty:
            return None, "No data found for this ticker"

        return data, None
    except Exception as e:
        return None, f"Error fetching data: {str(e)}"

def process_data(data):
    """Process data to add moving averages and candle colors"""
    # Calculate moving averages
    data['MA_9'] = data['Close'].rolling(window=9, min_periods=1).mean()
    data['MA_20'] = data['Close'].rolling(window=20, min_periods=1).mean()

    # Determine candle colors
    conditions = [
        data['Close'] > data['Open'],
        data['Close'] < data['Open']
    ]
    choices = ['green', 'red']
    data['Candle'] = np.select(conditions, choices, default='doji')

    # MA position analysis
    data['MA_Above'] = data['MA_9'] > data['MA_20']

    return data

def create_matplotlib_chart(data, ticker):
    """Create matplotlib chart"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                   gridspec_kw={'height_ratios': [3, 1]},
                                   sharex=True)

    # Price chart
    ax1.plot(data.index, data['Close'], label='Close Price', color='black', linewidth=2)
    ax1.plot(data.index, data['MA_9'], label='9-Period MA', color='blue', linewidth=1.5)
    ax1.plot(data.index, data['MA_20'], label='20-Period MA', color='orange', linewidth=1.5)

    # Add candlestick markers
    green_candles = data[data['Candle'] == 'green']
    red_candles = data[data['Candle'] == 'red']

    if not green_candles.empty:
        ax1.scatter(green_candles.index, green_candles['Close'], 
                   color='green', alpha=0.7, s=30, label='Green Candles', zorder=5)

    if not red_candles.empty:
        ax1.scatter(red_candles.index, red_candles['Close'], 
                   color='red', alpha=0.7, s=30, label='Red Candles', zorder=5)

    ax1.set_title(f'{ticker} Price with Moving Averages', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price (USD)', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Volume chart
    colors = ['green' if close > open_price else 'red' 
              for close, open_price in zip(data['Close'], data['Open'])]
    ax2.bar(data.index, data['Volume'], color=colors, alpha=0.6, width=0.8)
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.set_xlabel('Time', fontsize=12)
    ax2.grid(True, alpha=0.3)

    # Format x-axis
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig

def calculate_statistics(data):
    """Calculate hypothesis testing statistics"""
    if data.empty:
        return {}

    # Current values
    current_price = data['Close'].iloc[-1]
    ma9_current = data['MA_9'].iloc[-1]
    ma20_current = data['MA_20'].iloc[-1]

    # MA position analysis
    below_ma = data[data['MA_Above'] == False]
    above_ma = data[data['MA_Above'] == True]

    # Count candles by position
    green_below = len(below_ma[below_ma['Candle'] == 'green'])
    red_below = len(below_ma[below_ma['Candle'] == 'red'])
    green_above = len(above_ma[above_ma['Candle'] == 'green'])
    red_above = len(above_ma[above_ma['Candle'] == 'red'])

    # Calculate percentages
    total_below = green_below + red_below
    total_above = green_above + red_above

    green_below_pct = (green_below / total_below * 100) if total_below > 0 else 0
    red_below_pct = (red_below / total_below * 100) if total_below > 0 else 0
    green_above_pct = (green_above / total_above * 100) if total_above > 0 else 0
    red_above_pct = (red_above / total_above * 100) if total_above > 0 else 0

    return {
        'current_price': current_price,
        'ma9_current': ma9_current,
        'ma20_current': ma20_current,
        'green_below': green_below,
        'red_below': red_below,
        'green_above': green_above,
        'red_above': red_above,
        'green_below_pct': green_below_pct,
        'red_below_pct': red_below_pct,
        'green_above_pct': green_above_pct,
        'red_above_pct': red_above_pct,
        'total_below': total_below,
        'total_above': total_above
    }

# Main application
def main():
    # Fetch data
    with st.spinner(f"Fetching data for {ticker}..."):
        data, error = fetch_stock_data(ticker, period, interval)

    if error:
        st.error(f"❌ {error}")
        return

    if data is None or data.empty:
        st.warning("No data available for the selected ticker and period.")
        return

    # Process data
    data = process_data(data)

    # Calculate statistics
    stats = calculate_statistics(data)

    # Display current info
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Current Price", f"${stats['current_price']:.2f}")
    with col2:
        st.metric("9-Period MA", f"${stats['ma9_current']:.2f}")
    with col3:
        st.metric("20-Period MA", f"${stats['ma20_current']:.2f}")
    with col4:
        ma_status = "Above" if stats['ma9_current'] > stats['ma20_current'] else "Below"
        st.metric("9-MA vs 20-MA", ma_status)

    # Create and display matplotlib chart
    fig = create_matplotlib_chart(data, ticker)
    st.pyplot(fig)

    # Hypothesis Testing Results
    st.header("🧪 Hypothesis Testing Results")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("When 9-MA < 20-MA")
        if stats['total_below'] > 0:
            st.write(f"**Total Candles:** {stats['total_below']}")
            st.write(f"🟢 **Green Candles:** {stats['green_below']} ({stats['green_below_pct']:.1f}%)")
            st.write(f"🔴 **Red Candles:** {stats['red_below']} ({stats['red_below_pct']:.1f}%)")

            # Hypothesis validation
            if stats['red_below'] > stats['green_below']:
                st.success("✅ Hypothesis SUPPORTED: More red candles when 9-MA < 20-MA")
            else:
                st.warning("❌ Hypothesis NOT SUPPORTED: More green candles when 9-MA < 20-MA")
        else:
            st.info("No data available for this condition")

    with col2:
        st.subheader("When 9-MA > 20-MA") 
        if stats['total_above'] > 0:
            st.write(f"**Total Candles:** {stats['total_above']}")
            st.write(f"🟢 **Green Candles:** {stats['green_above']} ({stats['green_above_pct']:.1f}%)")
            st.write(f"🔴 **Red Candles:** {stats['red_above']} ({stats['red_above_pct']:.1f}%)")

            # Hypothesis validation
            if stats['green_above'] > stats['red_above']:
                st.success("✅ Hypothesis SUPPORTED: More green candles when 9-MA > 20-MA")
            else:
                st.warning("❌ Hypothesis NOT SUPPORTED: More red candles when 9-MA > 20-MA")
        else:
            st.info("No data available for this condition")

    # Summary Statistics Table
    st.header("📊 Summary Statistics")
    summary_data = {
        'Condition': ['9-MA Below 20-MA', '9-MA Above 20-MA'],
        'Total Candles': [stats['total_below'], stats['total_above']],
        'Green Candles': [f"{stats['green_below']} ({stats['green_below_pct']:.1f}%)", 
                         f"{stats['green_above']} ({stats['green_above_pct']:.1f}%)"],
        'Red Candles': [f"{stats['red_below']} ({stats['red_below_pct']:.1f}%)", 
                       f"{stats['red_above']} ({stats['red_above_pct']:.1f}%)"]
    }
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)

    # Data table
    with st.expander("📊 Raw Data (Last 50 Records)"):
        display_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'MA_9', 'MA_20', 'Candle', 'MA_Above']
        st.dataframe(data[display_cols].tail(50), use_container_width=True)

    # Last update time
    st.sidebar.markdown(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")

    # Auto-refresh
    if auto_refresh:
        time.sleep(30)
        st.rerun()

# Run the app
if __name__ == "__main__":
    main()
