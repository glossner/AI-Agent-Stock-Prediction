import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

class DataFetcher:
    def __init__(self, start_date: datetime = None):
        if start_date is None:
            self.start_date = datetime.today() - timedelta(days=365)
        else:
            self.start_date = start_date

    def get_stock_data(self, symbol: str, start_date: datetime = None, max_retries: int = 3) -> pd.DataFrame:
        if start_date is None:
            start_date = self.start_date

        end_date = datetime.today()
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        for attempt in range(max_retries):
            try:
                df = yf.download(symbol, start=start_date_str, end=end_date_str)
                if df.empty:
                    raise ValueError(f"No data retrieved for {symbol}")
                df.index = pd.to_datetime(df.index)
                return df
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: Error fetching data for {symbol}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait for 2 seconds before retrying
                else:
                    print(f"Failed to fetch data for {symbol} after {max_retries} attempts")
                    raise

    def get_realtime_price(self, symbol: str, max_retries: int = 3) -> float:
        for attempt in range(max_retries):
            try:
                ticker = yf.Ticker(symbol)
                return ticker.info['regularMarketPrice']
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: Error fetching real-time price for {symbol}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait for 2 seconds before retrying
                else:
                    print(f"Failed to fetch real-time price for {symbol} after {max_retries} attempts")
                    raise

    def schedule_updates(self, symbol: str, interval: int = 60):
        # This is a placeholder for scheduling regular updates
        # In a real implementation, you might use a task scheduler like APScheduler
        print(f"Scheduled updates for {symbol} every {interval} seconds")

# Example usage
if __name__ == "__main__":
    fetcher = DataFetcher()
    try:
        data = fetcher.get_stock_data("AAPL")
        print(data.tail())
        price = fetcher.get_realtime_price("AAPL")
        print(f"Current price of AAPL: ${price}")
        fetcher.schedule_updates("AAPL")
    except Exception as e:
        print(f"An error occurred: {str(e)}")