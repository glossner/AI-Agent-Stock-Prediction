import sys
import os
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.Data_Retrieval.data_fetcher import DataFetcher
from src.Agents.Agent_Indicators.indicator_agent_sma import SMAIndicator
from src.Agents.Analysis.trend_detection_agent import TrendDetectionAgent
from src.Agents.Analysis.trend_prediction_agent import TrendPredictionAgent
from src.Agents.Analysis.signal_generation_agent import SignalGenerationAgent
from src.Data_Retrieval.data_fetcher import DataFetcher
from src.Agents.Agent_Indicators.indicator_agent_sma import SMAIndicator
from src.Agents.Agent_Indicators.indicator_agent_rsi import RSIIndicator

# Set page config
st.set_page_config(page_title="Advanced Stock Analysis System", page_icon="📈", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize agents
@st.cache_resource
def load_agents():
    return (
        DataFetcher(),
        SMAIndicator(),
        RSIIndicator(),
        TrendDetectionAgent(),
        TrendPredictionAgent(),
        SignalGenerationAgent(
            trend_detection_agent=TrendDetectionAgent(),
            trend_prediction_agent=TrendPredictionAgent()
        )
    )

data_fetcher, sma_indicator, rsi_indicator, trend_detection_agent, trend_prediction_agent, signal_generation_agent = load_agents()

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Technical Analysis", "Trend Analysis", "Signal Generation"])

# Main content
st.title("Advanced Stock Analysis System 📈")

# Input field to choose stock symbol
symbol = st.text_input("Enter Stock Symbol:", value="AAPL")

@st.cache_data
def load_data(symbol):
    return data_fetcher.get_stock_data(symbol)

try:
    data = load_data(symbol)

    if page == "Home":
        st.header(f"Overview for {symbol}")
        
        # Display basic stock info
        stock = yf.Ticker(symbol)
        info = stock.info
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
        col2.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}")
        col3.metric("52 Week High", f"${info.get('fiftyTwoWeekHigh', 'N/A')}")

        # Plot stock price
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price'))
        fig.update_layout(title=f"{symbol} Stock Price", xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig, use_container_width=True)

        # Display recent data
        st.subheader("Recent Data")
        st.dataframe(data.tail())

    elif page == "Technical Analysis":
        st.header("Technical Analysis")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Calculate SMA"):
                period = st.slider("SMA Period", min_value=5, max_value=200, value=50)
                sma_indicator.period = period
                data_with_sma = sma_indicator.calculate(data)
                sma_column = f"SMA_{period}"
                
                if sma_column not in data_with_sma.columns:
                    st.error(f"SMA column '{sma_column}' not found. Available columns: {', '.join(data_with_sma.columns)}")
                else:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price'))
                    fig.add_trace(go.Scatter(x=data.index, y=data_with_sma[sma_column], name=f'SMA{period}'))
                    fig.update_layout(title=f"SMA{period} Analysis", xaxis_title="Date", yaxis_title="Price")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    analysis = sma_indicator.analyze(data_with_sma)
                    st.markdown(f"**SMA Analysis:**")
                    st.markdown(f"- Trend: {analysis['trend']}")
                    st.markdown(f"- Current Price: ${analysis['current_price']:.2f}")
                    st.markdown(f"- SMA Value: ${analysis['sma_value']:.2f}")

        with col2:
            if st.button("Calculate RSI"):
                period = st.slider("RSI Period", min_value=5, max_value=50, value=14)
                rsi_indicator.period = period
                data_with_rsi = rsi_indicator.calculate(data)
                rsi_column = f"RSI_{period}"
                
                if rsi_column not in data_with_rsi.columns:
                    st.error(f"RSI column '{rsi_column}' not found. Available columns: {', '.join(data_with_rsi.columns)}")
                else:
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
                    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=data.index, y=data_with_rsi[rsi_column], name=f'RSI{period}'), row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                    fig.update_layout(title=f"RSI{period} Analysis", xaxis_title="Date", yaxis_title="Price")
                    fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    analysis = rsi_indicator.analyze(data_with_rsi)
                    st.markdown(f"**RSI Analysis:**")
                    st.markdown(f"- Condition: {analysis['condition']}")
                    st.markdown(f"- Current Price: ${analysis['current_price']:.2f}")
                    st.markdown(f"- RSI Value: {analysis['rsi_value']:.2f}")

    elif page == "Trend Analysis":
        st.header("Trend Analysis")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Detect Trend"):
                detected_trend = trend_detection_agent.analyze_trend(data)
                trend_strength = trend_detection_agent.get_trend_strength(data)
                trend_duration = trend_detection_agent.get_trend_duration(data)
                st.markdown(f"<p class='big-font'>Detected Trend: {detected_trend}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='big-font'>Trend Strength: {trend_strength:.2f}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='big-font'>Trend Duration: {trend_duration} periods</p>", unsafe_allow_html=True)

        with col2:
            if st.button("Predict Trend"):
                with st.spinner("Training models and predicting trend..."):
                    arima_trend, arima_confidence, arima_forecast = trend_prediction_agent.predict_trend(data, model_type='arima')
                    lstm_trend, lstm_confidence, lstm_forecast = trend_prediction_agent.predict_trend(data, model_type='lstm')
                    
                    st.markdown(f"<p class='big-font'>ARIMA predicts: {arima_trend} (Confidence: {arima_confidence:.2f})</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='big-font'>LSTM predicts: {lstm_trend} (Confidence: {lstm_confidence:.2f})</p>", unsafe_allow_html=True)
                    
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=("ARIMA Forecast", "LSTM Forecast"))
                    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Actual'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=arima_forecast.index, y=arima_forecast, name='ARIMA Forecast'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Actual'), row=2, col=1)
                    fig.add_trace(go.Scatter(x=lstm_forecast.index, y=lstm_forecast, name='LSTM Forecast'), row=2, col=1)
                    fig.update_layout(height=800, title_text="Trend Forecasts")
                    st.plotly_chart(fig, use_container_width=True)

    elif page == "Signal Generation":
        st.header("Signal Generation")

        if st.button("Generate Trading Signal"):
            with st.spinner("Generating trading signal..."):
                signal = signal_generation_agent.generate_signal(data, symbol)
                st.markdown("<p class='big-font'>Trading Signal:</p>", unsafe_allow_html=True)
                st.write(signal_generation_agent.format_signal_response(signal))
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price'))
                fig.add_hline(y=signal['price'], line_dash="dash", line_color="red", annotation_text="Current Price")
                if signal['stop_loss']:
                    fig.add_hline(y=signal['stop_loss'], line_dash="dot", line_color="orange", annotation_text="Stop Loss")
                if signal['take_profit']:
                    fig.add_hline(y=signal['take_profit'], line_dash="dot", line_color="green", annotation_text="Take Profit")
                fig.update_layout(title=f"Trading Signal for {symbol}", xaxis_title="Date", yaxis_title="Price")
                st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit")