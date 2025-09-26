# streamlit_stock_monitor_simple.py

import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time

from bollinger import add_bollinger_bands, detect_bband_big_moves

# Streamlit page setup
st.set_page_config(
    page_title="Real-Time Stock Monitor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 Real-Time Stock Monitor with Moving Averages and Bollinger Bands")
st.markdown("Live monitoring of stock prices. Select which hypothesis to show and zoom into price action.")

# Sidebar controls
st.sidebar.header("🎛️ Controls")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL", max_chars=10).upper()
period_options = {"1 Day": "1d", "5 Days": "5d", "1 Month": "1mo", "3 Months": "3mo"}
selected_period = st.sidebar.selectbox("Data Period", list(period_options.keys()), index=0)
period = period_options[selected_period]
interval_options = {"1 Minute": "1m", "2 Minutes": "2m", "5 Minutes": "5m", "15 Minutes": "15m", "1 Hour": "1h"}
selected_interval = st.sidebar.selectbox("Data Interval", list(interval_options.keys()), index=0)
interval = interval_options[selected_interval]
auto_refresh = st.sidebar.checkbox("Auto Refresh (30 seconds)", value=True)
if st.sidebar.button("🔄 Refresh Now"):
    st.rerun()

# Hypothesis toggles
st.sidebar.subheader("Select Hypothesis to Display")
show_ma_hypothesis = st.sidebar.checkbox("Show MA/Candle Color Hypothesis", value=True)
show_bband_hypothesis = st.sidebar.checkbox("Show Bollinger Band Hypothesis", value=True)

# Zoom option
st.sidebar.subheader("Zoom Options")
zoom_npoints = st.sidebar.slider("Show Last N Data Points on Chart", min_value=10, max_value=500, value=50, step=10)

@st.cache_data(ttl=30)
def fetch_stock_data(ticker, period, interval):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        if data.empty:
            return None, "No data found for this ticker"
        return data, None
    except Exception as e:
        return None, f"Error fetching data: {str(e)}"

def process_data(data):
    data['MA_9'] = data['Close'].rolling(window=9, min_periods=1).mean()
    data['MA_20'] = data['Close'].rolling(window=20, min_periods=1).mean()
    conditions = [
        data['Close'] > data['Open'],
        data['Close'] < data['Open']
    ]
    choices = ['green', 'red']
    data['Candle'] = np.select(conditions, choices, default='doji')
    data['MA_Above'] = data['MA_9'] > data['MA_20']
    return data

def create_matplotlib_chart(data, ticker):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9),
                                gridspec_kw={'height_ratios': [3, 1]},
                                sharex=True)
    # Price and MA lines
    ax1.plot(data.index, data['Close'], label='Close Price', color='black', linewidth=2)
    ax1.plot(data.index, data['MA_9'], label='9-Period MA', color='blue', linewidth=1.5)
    ax1.plot(data.index, data['MA_20'], label='20-Period MA', color='orange', linewidth=1.5)
    ax1.plot(data.index, data['BB_Upper'], label='BB Upper', color='purple', linestyle='--', linewidth=1)
    ax1.plot(data.index, data['BB_Lower'], label='BB Lower', color='brown', linestyle='--', linewidth=1)
    green_candles = data[data['Candle'] == 'green']
    red_candles = data[data['Candle'] == 'red']
    if not green_candles.empty:
        ax1.scatter(green_candles.index, green_candles['Close'], color='green', alpha=0.7, s=30, label='Green Candles', zorder=5)
    if not red_candles.empty:
        ax1.scatter(red_candles.index, red_candles['Close'], color='red', alpha=0.7, s=30, label='Red Candles', zorder=5)
    ax1.set_title(f'{ticker} Price with Moving Averages & Bollinger Bands', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price (USD)', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    colors = ['green' if close > open_price else 'red' for close, open_price in zip(data['Close'], data['Open'])]
    ax2.bar(data.index, data['Volume'], color=colors, alpha=0.6, width=0.8)
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.set_xlabel('Time', fontsize=12)
    ax2.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def calculate_statistics(data):
    if data.empty:
        return {}
    current_price = data['Close'].iloc[-1]
    ma9_current = data['MA_9'].iloc[-1]
    ma20_current = data['MA_20'].iloc[-1]
    below_ma = data[data['MA_Above'] == False]
    above_ma = data[data['MA_Above'] == True]
    green_below = len(below_ma[below_ma['Candle'] == 'green'])
    red_below = len(below_ma[below_ma['Candle'] == 'red'])
    green_above = len(above_ma[above_ma['Candle'] == 'green'])
    red_above = len(above_ma[above_ma['Candle'] == 'red'])
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

def main():
    with st.spinner(f"Fetching data for {ticker}..."):
        data, error = fetch_stock_data(ticker, period, interval)
    if error:
        st.error(f"❌ {error}")
        return
    if data is None or data.empty:
        st.warning("No data available for the selected ticker and period.")
        return
    data = process_data(data)
    data = add_bollinger_bands(data)
    stats = calculate_statistics(data)
    bband_stats = detect_bband_big_moves(data)

    # Zoom data for all chart/hypothesis
    display_data = data.tail(zoom_npoints)

    # Metrics
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

    # Chart
    fig = create_matplotlib_chart(display_data, ticker)
    st.pyplot(fig)

    # Hypothesis 1: MA
    if show_ma_hypothesis:
        st.header("🧪 Hypothesis 1: Moving Average Candle Colors")
        col1, col2 = st.columns(2)
        below_ma = display_data[display_data['MA_Above'] == False]
        above_ma = display_data[display_data['MA_Above'] == True]
        green_below = len(below_ma[below_ma['Candle'] == 'green'])
        red_below = len(below_ma[below_ma['Candle'] == 'red'])
        green_above = len(above_ma[above_ma['Candle'] == 'green'])
        red_above = len(above_ma[above_ma['Candle'] == 'red'])
        total_below = green_below + red_below
        total_above = green_above + red_above
        green_below_pct = (green_below / total_below * 100) if total_below > 0 else 0
        red_below_pct = (red_below / total_below * 100) if total_below > 0 else 0
        green_above_pct = (green_above / total_above * 100) if total_above > 0 else 0
        red_above_pct = (red_above / total_above * 100) if total_above > 0 else 0
        with col1:
            st.subheader("When 9-MA < 20-MA")
            if total_below > 0:
                st.write(f"**Candles (Zoomed):** {total_below}")
                st.write(f"🟢 **Green Candles:** {green_below} ({green_below_pct:.1f}%)")
                st.write(f"🔴 **Red Candles:** {red_below} ({red_below_pct:.1f}%)")
                if red_below > green_below:
                    st.success("✅ Hypothesis SUPPORTED: More red candles when 9-MA < 20-MA")
                else:
                    st.warning("❌ Hypothesis NOT SUPPORTED: More green candles when 9-MA < 20-MA")
            else:
                st.info("No data in zoom window for this condition")
        with col2:
            st.subheader("When 9-MA > 20-MA")
            if total_above > 0:
                st.write(f"**Candles (Zoomed):** {total_above}")
                st.write(f"🟢 **Green Candles:** {green_above} ({green_above_pct:.1f}%)")
                st.write(f"🔴 **Red Candles:** {red_above} ({red_above_pct:.1f}%)")
                if green_above > red_above:
                    st.success("✅ Hypothesis SUPPORTED: More green candles when 9-MA > 20-MA")
                else:
                    st.warning("❌ Hypothesis NOT SUPPORTED: More red candles when 9-MA > 20-MA")
            else:
                st.info("No data in zoom window for this condition")

    # Hypothesis 2: Bollinger Bands
    if show_bband_hypothesis:
        st.header("🧪 Hypothesis 2: Bollinger Band 'Big Move' Detection")
        big_move_above = display_data[display_data['Close'] > display_data['BB_Upper']]
        big_move_below = display_data[display_data['Close'] < display_data['BB_Lower']]
        total_big_moves = len(big_move_above) + len(big_move_below)
        st.write(f"Big moments in zoom window: **{total_big_moves}**")
        st.write(f"Moves above upper band: **{len(big_move_above)}**")
        st.write(f"Moves below lower band: **{len(big_move_below)}**")
        if total_big_moves > 0:
            st.success("✅ Bollinger Band Effect PRESENT in zoom window: 'Big moments' detected as price moves outside bands.")
        else:
            st.info("No Bollinger Band 'big moments' detected in zoom window.")

    # Raw Data Show/Hide
    with st.expander("📊 Raw Data (Zoomed Window)"):
        display_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'MA_9', 'MA_20', 'BB_Upper', 'BB_Lower', 'Candle', 'MA_Above']
        st.dataframe(display_data[display_cols], use_container_width=True)

    st.sidebar.markdown(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")
    if auto_refresh:
        time.sleep(30)
        st.rerun()

if __name__ == "__main__":
    main()
