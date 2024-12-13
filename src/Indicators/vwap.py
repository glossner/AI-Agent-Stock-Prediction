import pandas as pd

class VWAPIndicator:
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate VWAP using pandas.
        Args:
            data (pd.DataFrame): Stock data containing 'Close', 'High', 'Low', 'Volume', and a DateTime index.
        Returns:
            pd.DataFrame: DataFrame with VWAP and the original data.
        """
        # Ensure required columns are in the data
        required_columns = ['Close', 'High', 'Low', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(
                f"Data must contain {', '.join(required_columns)} columns. Missing: {', '.join(missing_columns)}"
            )

        # Remove duplicate columns
        data = data.loc[:, ~data.columns.duplicated()]

        # Ensure 'Volume' is numeric
        if not pd.api.types.is_numeric_dtype(data['Volume']):
            data['Volume'] = pd.to_numeric(data['Volume'], errors='coerce')
            if data['Volume'].isnull().any():
                raise ValueError("Non-numeric values found in 'Volume' column after conversion.")

        # Calculate Typical Price
        data['Typical Price'] = (data['High'] + data['Low'] + data['Close']) / 3

        # Ensure 'Typical Price' is numeric
        if not pd.api.types.is_numeric_dtype(data['Typical Price']):
            data['Typical Price'] = pd.to_numeric(data['Typical Price'], errors='coerce')
            if data['Typical Price'].isnull().any():
                raise ValueError("Non-numeric values found in 'Typical Price' column after conversion.")

        # Ensure the DataFrame index is a DateTimeIndex
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("DataFrame index must be a DatetimeIndex.")

        # Create a 'TradingDate' column to group by each trading day
        data['TradingDate'] = data.index.date

        # Function to calculate VWAP for each group (trading day)
        def calculate_vwap(group):
            cumulative_tpv = (group['Typical Price'] * group['Volume']).cumsum()
            cumulative_volume = group['Volume'].cumsum()
            group['VWAP'] = cumulative_tpv / cumulative_volume
            return group

        # Apply the function to each trading day
        data = data.groupby('TradingDate', group_keys=False).apply(calculate_vwap)

        # Drop the 'TradingDate' column as it's no longer needed
        data.drop(columns=['TradingDate'], inplace=True)

        # Return only the VWAP and Close columns
        return data[['VWAP', 'Close']]


