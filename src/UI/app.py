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
from src.Data_Retrieval.data_fetcher import DataFetcher
from src.Agents.Agent_Indicators.indicator_agent_sma import SMAIndicator
from src.Agents.Analysis.trend_prediction_agent import TrendPredictionAgent
from src.globals import gpt_model
from langchain.schema import HumanMessage

# Initialize agents
data_fetcher = DataFetcher()
trend_prediction_agent = TrendPredictionAgent()

# Function to generate AI analysis
def generate_ai_analysis(data, symbol):
    if gpt_model is None:
        return "AI analysis is not available due to model initialization error."

    last_price = data['Close'].iloc[-1]
    price_change = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0] * 100
    volume = data['Volume'].iloc[-1]
    
    prompt = f"""
    Analyze the following stock data for {symbol}:
    - Last closing price: ${last_price:.2f}
    - Price change over the period: {price_change:.2f}%
    - Latest trading volume: {volume}

    Please provide a brief analysis of this stock based on these metrics. 
    Consider factors like recent performance, volume trends, and potential future outlook.
    Limit your response to 3-4 sentences.
    """

    try:
        response = gpt_model.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        return f"An error occurred while generating AI analysis: {str(e)}"

# Streamlit UI
st.title("Advanced Stock Analysis System")

# Input field to choose stock symbol
symbol = st.text_input("Enter Stock Symbol:", value="AAPL")

try:
    # Initialize the DataFetcher and retrieve the data
    data = data_fetcher.get_stock_data(symbol)

    # Display the original data
    st.write(f"Original Stock Data for {symbol}:")
    st.dataframe(data.tail())

    # Technical Analysis Section
    st.header("Technical Analysis")

    if st.button("Calculate SMA"):
        try:
            period = st.number_input("Enter SMA period:", min_value=1, max_value=100, value=14)
            sma_indicator = SMAIndicator(period=period)
            data_with_sma = sma_indicator.calculate(data)
            st.write(f"Stock Data with SMA{period} for {symbol}:")
            st.dataframe(data_with_sma.tail())
            sma_analysis = sma_indicator.respond(data)
            st.write(sma_analysis)
        except Exception as e:
            st.error(f"Error calculating SMA: {str(e)}")

    if st.button("Calculate RSI"):
        try:
            period = st.number_input("Enter RSI period:", min_value=1, max_value=100, value=14)
            data[f"RSI{period}"] = ta.rsi(data['Close'], length=period)
            st.write(f"Stock Data with RSI{period} for {symbol}:")
            st.dataframe(data.tail())
        except Exception as e:
            st.error(f"Error calculating RSI: {str(e)}")

    # Trend Prediction Section
    st.header("Trend Prediction")

    if st.button("Predict Trend"):
        if len(data) < 100:
            st.warning("Not enough data for trend prediction. Please fetch more historical data.")
        else:
            try:
                with st.spinner("Training models and predicting trend..."):
                    # Train ARIMA model
                    trend_prediction_agent.train_arima(data)
                    arima_trend, arima_forecast = trend_prediction_agent.predict_trend(data, model_type='arima')
                    
                    # Train LSTM model
                    trend_prediction_agent.train_lstm(data)
                    lstm_trend, lstm_prediction = trend_prediction_agent.predict_trend(data, model_type='lstm')
                    
                    st.write(f"ARIMA predicts: {arima_trend}")
                    st.write(f"LSTM predicts: {lstm_trend}")
                    
                    # Plot forecasts
                    st.subheader("ARIMA Forecast")
                    last_date = data.index[-1]
                    forecast_index = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=len(arima_forecast))
                    forecast_df = pd.DataFrame({'Forecast': arima_forecast}, index=forecast_index)
                    plot_df = pd.concat([data['Close'].rename('Actual')[-30:], forecast_df])
                    st.line_chart(plot_df)
                    
                    st.subheader("LSTM Forecast")
                    future_dates = pd.date_range(start=data.index[-1], periods=31, freq='D')[1:]
                    lstm_forecast = pd.Series(lstm_prediction, index=future_dates)
                    lstm_plot_df = pd.concat([data['Close'].rename('Actual')[-30:], lstm_forecast.rename('Forecast')])
                    st.line_chart(lstm_plot_df)
            except Exception as e:
                st.error(f"Error predicting trend: {str(e)}")

    if st.button("Evaluate Models"):
        try:
            with st.spinner("Evaluating models..."):
                arima_rmse = trend_prediction_agent.evaluate_model(data, model_type='arima')
                lstm_rmse = trend_prediction_agent.evaluate_model(data, model_type='lstm')
                
                st.write(f"ARIMA RMSE: {arima_rmse:.2f}")
                st.write(f"LSTM RMSE: {lstm_rmse:.2f}")
        except Exception as e:
            st.error(f"Error evaluating models: {str(e)}")

    if st.button("Optimize Models"):
        try:
            with st.spinner("Optimizing models... This may take a while."):
                best_arima_params = trend_prediction_agent.optimize_model(data, model_type='arima')
                best_lstm_params = trend_prediction_agent.optimize_model(data, model_type='lstm')
                
                st.write("Best ARIMA parameters:")
                st.write(best_arima_params)
                st.write("Best LSTM parameters:")
                st.write(best_lstm_params)
        except Exception as e:
            st.error(f"Error optimizing models: {str(e)}")

            

    # AI Analysis Section
    st.header("AI-Powered Analysis")

    if st.button("Get AI Analysis"):
        try:
            with st.spinner("Generating AI analysis..."):
                analysis = generate_ai_analysis(data, symbol)
                st.write("AI Analysis:")
                st.write(analysis)
        except Exception as e:
            st.error(f"Error generating AI analysis: {str(e)}")

    # Add a button to fetch the latest data for the selected symbol
    if st.button("Fetch Latest Data"):
        try:
            latest_data = data_fetcher.get_stock_data(symbol)
            st.write(f"Latest Stock Data for {symbol}:")
            st.dataframe(latest_data.tail())
        except Exception as e:
            st.error(f"Error fetching latest data: {str(e)}")

except Exception as e:
    st.error(f"An error occurred while fetching data for {symbol}: {str(e)}")