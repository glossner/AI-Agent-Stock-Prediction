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
        close_prices = self.price_data['Close'].values  # Ensure it's an array of scalars
        indicator_values = self.indicator_data[self.indicator_name].values  # Ensure it's an array of scalars

        for i in range(1, len(close_prices)):
            if close_prices[i] < close_prices[i - 1] and indicator_values[i] > indicator_values[i - 1]:
                bullish_signals.append(self.price_data.index[i])  # Use the index for the date

        return bullish_signals


    def detect_bearish_divergence(self) -> list:
        """
        Detect bearish divergence between price and the indicator.

        Returns:
            List of dates where bearish divergence occurs.
        """
        bearish_signals = []
        close_prices = self.price_data['Close'].values
        indicator_values = self.indicator_data[self.indicator_name].values

        for i in range(1, len(close_prices)):
            if close_prices[i] > close_prices[i - 1] and indicator_values[i] < indicator_values[i - 1]:
                bearish_signals.append(self.price_data.index[i])  # Use the index for the date

        return bearish_signals