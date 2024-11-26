# src/Data_Retrieval/data_fetcher.py

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self, start_date: datetime = None, end_date: datetime = None):
        """
        Initializes the DataFetcher with a default start date of 30 days ago.

        Args:
            start_date (datetime, optional): The start date for data retrieval. Defaults to 30 days ago.
            end_date (datetime, optional): The end date for data retrieval. Defaults to today.
        """
        if start_date is None:
            # Set default start date to 30 days ago if not provided
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

        Args:
            symbol (str): The stock symbol to fetch data for.
            start_date (datetime, optional): The start date for data retrieval. If None, uses self.start_date.
            end_date (datetime, optional): The end date for data retrieval. If None, uses self.end_date.

        Returns:
            pd.DataFrame: A DataFrame containing the historical stock data with single-level columns.
        """
        # Ensure symbol is a single string
        symbol = str(symbol)

        # Use the provided start_date or fall back to self.start_date
        if start_date is None:
            start_date = self.start_date

        if end_date is None:
            end_date = self.end_date

        # Format dates as strings
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Download data for single symbol
        df = yf.download(symbol, start=start_date_str, end=end_date_str, auto_adjust=False)

        if df.empty:
            return df

        # Ensure single-level columns
        if isinstance(df.columns, pd.MultiIndex):
            # This should not happen for single symbol, but handle just in case
            df.columns = [col[0] for col in df.columns]
        else:
            # If single-level, ensure proper naming
            df.columns = [col.strip() for col in df.columns]

        return df
