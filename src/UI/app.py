import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import pandas as pd
from src.Data_Retrieval.data_fetcher import DataFetcher
from src.Indicators.sma import SMAIndicator  # Import the SMAIndicator class
import pandas_ta as ta

# Streamlit UI
st.title("Prototype Trading System")

# Input field to choose stock symbol
symbol = st.text_input("Enter Stock Symbol:", value="AAPL")

# Initialize the DataFetcher and retrieve the data
data_fetcher = DataFetcher()
data = data_fetcher.get_stock_data(symbol)

# Display the original data
st.write(f"Original Stock Data for {symbol}:")
st.dataframe(data.tail())

# Add a button to calculate and display SMA using SMAIndicator class
if st.button("Calculate SMA"):
    period = st.number_input("Enter SMA period:", min_value=1, max_value=100, value=14)
    sma_indicator = SMAIndicator(period=period)  # Instantiate the SMAIndicator class
    data_with_sma = sma_indicator.calculate(data)  # Calculate the SMA
    st.write(f"Stock Data with SMA{period} for {symbol}:")
    st.dataframe(data_with_sma.tail())

# Add a button to calculate and display RSI using pandas_ta
if st.button("Calculate RSI"):
    period = st.number_input("Enter RSI period:", min_value=1, max_value=100, value=14)
    data[f"RSI{period}"] = ta.rsi(data['Close'], length=period)
    st.write(f"Stock Data with RSI{period} for {symbol}:")
    st.dataframe(data.tail())

# Add a button to fetch the latest data for the selected symbol
if st.button("Fetch Latest Data"):
    latest_data = data_fetcher.get_stock_data(symbol)
    st.write(f"Latest Stock Data for {symbol}:")
    st.dataframe(latest_data.tail())
