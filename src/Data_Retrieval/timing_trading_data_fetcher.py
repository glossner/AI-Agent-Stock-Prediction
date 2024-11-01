import yfinance as yf
from datetime import datetime

class DataFetcher:
    def get_earnings_date(self, stock):
        ticker = yf.Ticker(stock)
        try:
            # Use get_earnings_dates to retrieve earnings dates directly
            earnings_dates = ticker.get_earnings_dates()
            
            # Filter for dates before today to get the most recent past earnings date
            past_earnings_dates = earnings_dates[earnings_dates.index < datetime.today().strftime('%Y-%m-%d')]
            if not past_earnings_dates.empty:
                last_earnings_date = past_earnings_dates.index[0]  # Most recent past date
                return last_earnings_date.strftime('%Y-%m-%d')
            else:
                return "Last earnings date not found."
        except Exception as e:
            print(f"Error fetching last earnings date: {e}")
            return "Error fetching last earnings date."
