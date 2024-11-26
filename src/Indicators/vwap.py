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
        # Debug: Initial DataFrame info
        print("Initial DataFrame shape:", data.shape)
        print("Initial DataFrame columns:", data.columns.tolist())

        # Ensure required columns are in the data
        required_columns = ['Close', 'High', 'Low', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Data must contain {', '.join(required_columns)} columns. Missing: {', '.join(missing_columns)}")

        # Remove duplicate columns
        data = data.loc[:, ~data.columns.duplicated()]
        print("Columns after removing duplicates:", data.columns.tolist())

        # Validate 'Volume' column
        if isinstance(data['Volume'], pd.DataFrame):
            raise ValueError("'Volume' column is duplicated or has multiple columns.")
        
        # Ensure 'Volume' is numeric
        if not pd.api.types.is_numeric_dtype(data['Volume']):
            print("Converting 'Volume' to numeric.")
            data['Volume'] = pd.to_numeric(data['Volume'], errors='coerce')
            if data['Volume'].isnull().any():
                raise ValueError("Non-numeric values found in 'Volume' column after conversion.")

        # Calculate Typical Price
        data['Typical Price'] = (data['High'] + data['Low'] + data['Close']) / 3
        print("Typical Price calculated.")

        # Ensure 'Typical Price' is numeric
        if not pd.api.types.is_numeric_dtype(data['Typical Price']):
            print("Converting 'Typical Price' to numeric.")
            data['Typical Price'] = pd.to_numeric(data['Typical Price'], errors='coerce')
            if data['Typical Price'].isnull().any():
                raise ValueError("Non-numeric values found in 'Typical Price' column after conversion.")

        # Calculate VWAP using .loc to ensure single column assignment
        try:
            vwap_series = (data['Typical Price'] * data['Volume']).cumsum() / data['Volume'].cumsum()
            print("VWAP series calculated successfully.")
        except Exception as e:
            print("Error during VWAP calculation:", e)
            raise

        # Assign VWAP using .loc
        data.loc[:, 'VWAP'] = vwap_series
        print("VWAP assigned to DataFrame.")

        # Final DataFrame info
        print("Final DataFrame columns:", data.columns.tolist())
        print("Final DataFrame head:\n", data.head())

        # Return only the VWAP and Close columns
        return data[['VWAP', 'Close']]
