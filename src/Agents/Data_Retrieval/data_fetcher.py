import yfinance as yf
import pandas as pd

class DataFetcher:
    def __init__(self):
        pass

    def get_stock_data(self, symbol: str, start_date="2020-01-01") -> pd.DataFrame:
        """
        Fetches historical stock data for the given symbol.

        Args:
            symbol (str): The stock symbol to fetch data for.
            start_date (str): The start date for the data retrieval in YYYY-MM-DD format.

        Returns:
            pd.DataFrame: A DataFrame containing the historical stock data.
        """
        df = yf.download(symbol, start=start_date)
        df.index = pd.to_datetime(df.index)
        return df
