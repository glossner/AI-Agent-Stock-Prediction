import pandas as pd

class RSIIndicator:
    def __init__(self, period=14):
        """
        Initializes the RSIIndicator class with a given period.

        Args:
            period (int): The lookback period for RSI (default is 14).
        """
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the Relative Strength Index (RSI) for the given price data.

        Args:
            data (pd.DataFrame): A DataFrame containing stock prices (must have a 'Close' column).

        Returns:
            pd.DataFrame: A DataFrame with the calculated RSI.
        """
        # Ensure 'Close' column is available in the data
        if 'Close' not in data.columns:
            raise ValueError("Data must contain 'Close' prices.")

        # Calculate price differences
        delta = data['Close'].diff()

        # Split gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # Calculate the rolling average gain and loss
        avg_gain = gain.rolling(window=self.period, min_periods=1).mean()
        avg_loss = loss.rolling(window=self.period, min_periods=1).mean()

        # Calculate RS (Relative Strength) and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Flatten RSI to ensure it is 1-dimensional
        rsi = rsi.values.flatten()

        # Return RSI as a DataFrame with the same index
        result = pd.DataFrame({'RSI': rsi}, index=data.index)

        return result
