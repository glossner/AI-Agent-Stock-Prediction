import pandas as pd

class CommodityCorrelationIndicator:
    def __init__(self, stock_data, commodity_data):
        self.stock_data = stock_data
        self.commodity_data = commodity_data

    def calculate(self) -> float:
        return self.stock_data['Close'].corr(self.commodity_data['Close'])
