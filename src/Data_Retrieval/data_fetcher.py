import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self, start_date: datetime = None, end_date: datetime = None):
        """
        Initializes the DataFetcher with a default start date of 30 days ago.

        Args:
            start_date (datetime, optional): The start date for data retrieval. Defaults to 30 days ago.
        """
        if start_date is None:
            # Set default start date to 30 days ago if not provided
            self.start_date = datetime.today() - timedelta(days=60)
        else:
            self.start_date = start_date

        if end_date is None:
            self.end_date = datetime.today()

    def get_stock_data(self, symbol: str, start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
        """
        Fetches historical stock data for the given symbol.

        Args:
            symbol (str): The stock symbol to fetch data for.
            start_date (datetime, optional): The start date for data retrieval. If None, uses self.start_date.

        Returns:
            pd.DataFrame: A DataFrame containing the historical stock data.
        """
        # Use the provided start_date or fall back to self.start_date
        if start_date is None:
            start_date = self.start_date

        if end_date is None:
            end_date = datetime.today()

        # Format dates as strings
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Download data
        df = yf.download(symbol, start=start_date_str, end=end_date_str)
        df.index = pd.to_datetime(df.index)
        return df
