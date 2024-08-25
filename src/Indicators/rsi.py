import pandas as pd
import pandas_ta as ta

class RSIIndicator:
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        # Calculate the RSI and add it as a new column in the DataFrame
        rsi_column_name = f"RSI{self.period}"
        data[rsi_column_name] = ta.rsi(data['Close'], length=self.period)
        return data
