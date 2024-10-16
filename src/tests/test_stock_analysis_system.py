# File: src/tests/test_stock_analysis_system.py

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parents[2]
sys.path.append(str(project_root))

from src.Data_Retrieval.data_fetcher import DataFetcher
from src.Agents.Agent_Indicators.indicator_agent_sma import SMAIndicator
from src.Agents.Agent_Indicators.indicator_agent_rsi import RSIIndicator
from src.Agents.Analysis.trend_detection_agent import TrendDetectionAgent
from src.Agents.Analysis.trend_prediction_agent import TrendPredictionAgent
from src.Agents.Analysis.signal_generation_agent import SignalGenerationAgent

# Fixture for sample data
@pytest.fixture
def sample_data():
    dates = pd.date_range(start='1/1/2020', end='1/1/2021', freq='D')
    data = pd.DataFrame({
        'Open': np.random.randint(100, 200, size=len(dates)),
        'High': np.random.randint(150, 250, size=len(dates)),
        'Low': np.random.randint(50, 150, size=len(dates)),
        'Close': np.random.randint(100, 200, size=len(dates)),
        'Volume': np.random.randint(1000000, 5000000, size=len(dates))
    }, index=dates)
    return data

def test_sma_indicator(sample_data):
    sma_indicator = SMAIndicator(period=50)
    result = sma_indicator.calculate(sample_data)
    assert 'SMA_50' in result.columns
    # Check that we have NaN values at the beginning, but not at the end
    assert result['SMA_50'].head(49).isnull().all()
    assert not result['SMA_50'].tail(len(result) - 49).isnull().any()

def test_rsi_indicator(sample_data):
    rsi_indicator = RSIIndicator(period=14)
    result = rsi_indicator.calculate(sample_data)
    assert 'RSI_14' in result.columns
    # Check that we have NaN values at the beginning, but not at the end
    assert result['RSI_14'].head(14).isnull().all()
    assert not result['RSI_14'].tail(len(result) - 14).isnull().any()
    assert (result['RSI_14'].dropna() >= 0).all() and (result['RSI_14'].dropna() <= 100).all()


def test_trend_detection(sample_data):
    trend_detector = TrendDetectionAgent()
    trend = trend_detector.analyze_trend(sample_data)
    assert trend in ['Uptrend', 'Downtrend', 'Sideways']

def test_trend_prediction(sample_data):
    trend_predictor = TrendPredictionAgent()
    trend, confidence, forecast = trend_predictor.predict_trend(sample_data, model_type='arima')
    assert trend in ['Uptrend', 'Downtrend', 'Unknown']
    assert 0 <= confidence <= 1
    assert len(forecast) > 0

def test_signal_generation(sample_data):
    signal_generator = SignalGenerationAgent()
    signal = signal_generator.generate_signal(sample_data, 'SAMPLE')
    assert 'signal' in signal
    assert signal['signal'] in ['BUY', 'SELL', 'HOLD', 'STRONG BUY', 'STRONG SELL']

# Integration Tests

def test_end_to_end_analysis():
    data_fetcher = DataFetcher()
    sma_indicator = SMAIndicator()
    rsi_indicator = RSIIndicator()
    trend_detector = TrendDetectionAgent()
    trend_predictor = TrendPredictionAgent()
    signal_generator = SignalGenerationAgent()

    # Fetch data
    data = data_fetcher.get_stock_data('AAPL')

    # Calculate indicators
    data = sma_indicator.calculate(data)
    data = rsi_indicator.calculate(data)

    # Detect trend
    trend = trend_detector.analyze_trend(data)

    # Predict trend
    prediction, confidence, forecast = trend_predictor.predict_trend(data)

    # Generate signal
    signal = signal_generator.generate_signal(data, 'AAPL')

    assert 'SMA_50' in data.columns
    assert 'RSI_14' in data.columns
    assert trend in ['Uptrend', 'Downtrend', 'Sideways']
    assert prediction in ['Uptrend', 'Downtrend', 'Unknown']
    assert 'signal' in signal

# Performance Tests

@pytest.mark.parametrize("symbol", ['AAPL', 'GOOGL', 'MSFT'])
def test_data_fetcher_performance(symbol):
    data_fetcher = DataFetcher()
    start_time = datetime.now()
    data = data_fetcher.get_stock_data(symbol)
    end_time = datetime.now()
    assert (end_time - start_time) < timedelta(seconds=5)  # Assuming 5 seconds is an acceptable time

def test_signal_generation_performance(sample_data):
    signal_generator = SignalGenerationAgent()
    start_time = datetime.now()
    signal = signal_generator.generate_signal(sample_data, 'SAMPLE')
    end_time = datetime.now()
    assert (end_time - start_time) < timedelta(seconds=2)  # Assuming 2 seconds is an acceptable time

if __name__ == "__main__":
    pytest.main()