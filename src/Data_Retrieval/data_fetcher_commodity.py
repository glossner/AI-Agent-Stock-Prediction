import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self, start_date: datetime = None, end_date: datetime = None):
        """
        Initializes the DataFetcher with a default start date of 30 days ago.
        """
        if start_date is None:
            self.start_date = datetime.today() - timedelta(days=30)
        else:
            self.start_date = start_date

        if end_date is None:
            self.end_date = datetime.today()
        else:
            self.end_date = end_date

    def get_stock_data(self, symbol: str, start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
        """
        Fetches historical stock data for the given symbol.
        """
        if start_date is None:
            start_date = self.start_date

        if end_date is None:
            end_date = datetime.today()

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        df = yf.download(symbol, start=start_date_str, end=end_date_str)

        # Rename columns to include the stock ticker
        df = df.rename(columns=lambda col: f"{col}_{symbol}")
        df.index = pd.to_datetime(df.index)
        return df


    def get_commodity_data(self, commodity: str, start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
        commodity_symbols = {
            "OIL": "CL=F",     # Crude Oil WTI
            "GOLD": "GC=F"     # Gold
        }

        if commodity not in commodity_symbols:
            raise ValueError(f"Unsupported commodity: {commodity}")

        symbol = commodity_symbols[commodity]

        if start_date is None:
            start_date = self.start_date
        if end_date is None:
            end_date = datetime.today()

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        df = yf.download(symbol, start=start_date_str, end=end_date_str)

        # Ensure columns have a consistent name format
        df = df.rename(columns=lambda col: f"{col}_{commodity}")
        df.index = pd.to_datetime(df.index)
        return df
