# detect_divergence.py
import pandas as pd

class DivergenceDetector:
    def __init__(self, price_data: pd.DataFrame, indicator_data: pd.DataFrame, indicator_name: str):
        """
        Initialize the divergence detector.
        
        Args:
            price_data (pd.DataFrame): Stock price data with columns 'Close'.
            indicator_data (pd.DataFrame): Indicator data (MACD, RSI) with appropriate columns.
            indicator_name (str): Name of the indicator to detect divergence (e.g., 'MACD', 'RSI').
        """
        self.price_data = price_data
        self.indicator_data = indicator_data
        self.indicator_name = indicator_name

    def detect_bullish_divergence(self) -> list:
        """
        Detect bullish divergence between price and the indicator.
        
        Returns:
            List of dates where bullish divergence occurs.
        """
        bullish_signals = []
        # Compare lows: Price forms lower lows, but the indicator forms higher lows
        for i in range(1, len(self.price_data)):
            if self.price_data['Close'].iloc[i] < self.price_data['Close'].iloc[i-1] and \
               self.indicator_data[self.indicator_name].iloc[i] > self.indicator_data[self.indicator_name].iloc[i-1]:
                bullish_signals.append(self.price_data.index[i])
        return bullish_signals

    def detect_bearish_divergence(self) -> list:
        """
        Detect bearish divergence between price and the indicator.

        Returns:
            List of dates where bearish divergence occurs.
        """
        bearish_signals = []
        # Compare highs: Price forms higher highs, but the indicator forms lower highs
        for i in range(1, len(self.price_data)):
            if self.price_data['Close'].iloc[i] > self.price_data['Close'].iloc[i-1] and \
               self.indicator_data[self.indicator_name].iloc[i] < self.indicator_data[self.indicator_name].iloc[i-1]:
                bearish_signals.append(self.price_data.index[i])
        return bearish_signals
