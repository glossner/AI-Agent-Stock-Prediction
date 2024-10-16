import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time
import schedule
from src.Agents.base_agent import BaseAgent

class DataAcquisitionAgent(BaseAgent):
    def __init__(self, symbol: str, **kwargs):
        super().__init__(
            role='Data Acquisition Agent',
            goal='Fetch and manage real-time and historical market data',
            backstory='Expert in retrieving and processing financial data from various sources',
            **kwargs
        )
        self.symbol = symbol
        self.data = None
        self.last_update = None

    def fetch_historical_data(self, start_date: datetime = None, end_date: datetime = None, retries: int = 3):
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()

        for attempt in range(retries):
            try:
                data = yf.download(self.symbol, start=start_date, end=end_date)
                self.data = data
                self.last_update = datetime.now()
                return data
            except Exception as e:
                print(f"Error fetching data (attempt {attempt + 1}): {str(e)}")
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff

    def fetch_real_time_data(self):
        ticker = yf.Ticker(self.symbol)
        return ticker.info

    def normalize_data(self):
        if self.data is not None:
            # Ensure all column names are standardized
            self.data.columns = [col.lower() for col in self.data.columns]
            # Add any additional normalization steps here

    def update_data(self):
        last_date = self.data.index[-1].date() if self.data is not None else None
        today = datetime.now().date()

        if last_date != today:
            new_data = self.fetch_historical_data(start_date=last_date + timedelta(days=1))
            if not new_data.empty:
                self.data = pd.concat([self.data, new_data])
                self.normalize_data()

    def schedule_updates(self, interval_minutes=60):
        schedule.every(interval_minutes).minutes.do(self.update_data)

    def run_scheduled_updates(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

# Example usage
if __name__ == "__main__":
    agent = DataAcquisitionAgent("AAPL")
    historical_data = agent.fetch_historical_data()
    print(historical_data.tail())

    real_time_data = agent.fetch_real_time_data()
    print(real_time_data)

    agent.schedule_updates(interval_minutes=15)
    agent.run_scheduled_updates()