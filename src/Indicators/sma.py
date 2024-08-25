import pandas as pd
import pandas_ta as ta

class SMAIndicator:
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        # Calculate the SMA and add it as a new column in the DataFrame
        sma_column_name = f"SMA{self.period}"
        data[sma_column_name] = ta.sma(data['Close'], length=self.period)
        return data

    def respond(self, data: pd.DataFrame) -> pd.DataFrame:
        # Call the calculate method and return the updated DataFrame
        return self.calculate(data)
