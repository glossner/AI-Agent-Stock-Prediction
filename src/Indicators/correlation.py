      
import pandas as pd
import pandas_ta as ta

class CorrelationIndicator:
    def __init__(self, stock1_data, stock2_data):
        self.stock1_data = stock1_data
        self.stock2_data = stock2_data

    def calculate(self, data: pd.DataFrame) -> float:
        # Calculate the Correlation Coefficient
        return self.stock1_data['Close'].corr(self.stock2_data['Close'])
       