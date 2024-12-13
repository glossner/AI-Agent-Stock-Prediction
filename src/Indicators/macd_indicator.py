import pandas as pd

class MACDIndicator:
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        """
        Initializes the MACDIndicator class with given periods.

        Args:
            fast_period (int): The short EMA period for MACD (default is 12).
            slow_period (int): The long EMA period for MACD (default is 26).
            signal_period (int): The period for the signal line (default is 9).
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Compute MACD values from the given price data.

        Args:
            data (pd.DataFrame): A DataFrame containing stock prices (must have a 'Close' column).

        Returns:
            pd.DataFrame: A DataFrame with MACD Line, Signal Line, and MACD Histogram.
        """
        # Ensure 'Close' column is available in the data
        if 'Close' not in data.columns:
            raise ValueError("Data must contain 'Close' prices.")

        # Calculate the fast EMA (12-period EMA)
        ema_fast = data['Close'].ewm(span=self.fast_period, adjust=False).mean()

        # Calculate the slow EMA (26-period EMA)
        ema_slow = data['Close'].ewm(span=self.slow_period, adjust=False).mean()

        # MACD line: difference between fast and slow EMAs
        macd_line = ema_fast - ema_slow

        # Signal line: EMA of the MACD line
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()

        # MACD histogram: difference between MACD line and Signal line
        macd_histogram = macd_line - signal_line

        # Flatten the arrays to ensure 1D
        macd_line = macd_line.values.flatten()
        signal_line = signal_line.values.flatten()
        macd_histogram = macd_histogram.values.flatten()

        # Ensure the result has the same index as the original data
        result = pd.DataFrame({
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': macd_histogram
        }, index=data.index)  # Use the same index as the input data

        return result