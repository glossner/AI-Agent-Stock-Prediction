import streamlit as st
import os
import sys

# Debugging information
st.write(f"Current working directory: {os.getcwd()}")
st.write(f"sys.path: {sys.path}")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.Agents.Agent_Indicators.indicator_agent_rsi import IndicatorAgentRSI
from src.Agents.Agent_Indicators.indicator_agent_sma import IndicatorAgentSMA
from src.Agents.Data_Retrieval.data_fetcher import DataFetcher



# Initialize agents with your OpenAI API key
rsi_agent = IndicatorAgentRSI()
sma_agent = IndicatorAgentSMA()
data_fetcher = DataFetcher()

# Streamlit UI
st.title("Prototype Trading System")

# User input
symbol = st.text_input("Enter Stock Symbol:", "AAPL")

if st.button("Fetch Data"):
    data = data_fetcher.get_stock_data(symbol)
    st.write("Stock Data:")
    st.write(data.tail())

if st.button("Calculate RSI"):
    data = data_fetcher.get_stock_data(symbol)
    rsi = rsi_agent.respond(data.to_dict())
    st.write("RSI:")
    st.write(rsi[-5:])

if st.button("Calculate SMA"):
    data = data_fetcher.get_stock_data(symbol)
    sma = sma_agent.respond(data.to_dict())
    st.write("SMA:")
    st.write(sma[-5:])
