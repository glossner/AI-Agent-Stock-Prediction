import pandas as pd

class VWAPIndicator:
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate VWAP using pandas.
        Args:
            data (pd.DataFrame): Stock data containing 'Close', 'High', 'Low', and 'Volume' columns.
        Returns:
            pd.DataFrame: DataFrame with VWAP and the original data.
        """
        # Ensure required columns are in the data
        if not all(col in data.columns for col in ['Close', 'High', 'Low', 'Volume']):
            raise ValueError("Data must contain 'Close', 'High', 'Low', and 'Volume' columns.")

        # Calculate Typical Price
        data['Typical Price'] = (data['High'] + data['Low'] + data['Close']) / 3

        # Calculate VWAP
        data['VWAP'] = (data['Typical Price'] * data['Volume']).cumsum() / data['Volume'].cumsum()

        return data[['VWAP', 'Close']]
