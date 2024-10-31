import logging
import numpy as np
import pandas as pd
from yahooquery import Ticker
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from dotenv import load_dotenv

# Load environment variables (e.g., API keys)
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class DividendBacktester:
    def __init__(self, company, forecasted_growth=None):
        self.company = company
        self.forecasted_growth = forecasted_growth or [5, 5, 5, 5, 5]  # Example: 5% growth over 5 years

    def fetch_financial_data(self):
        logging.info(f"Fetching financial data for {self.company}...")
        ticker = Ticker(self.company)
        income_statement = ticker.income_statement(frequency='a')  # Get annual income statement
        cash_flow_statement = ticker.cash_flow(frequency='a')  # Get annual cash flow statement

        return {
            "IncomeStatement": income_statement.to_string(),
            "CashFlowStatement": cash_flow_statement.to_string()
        }


    def fetch_dividend_history(self):
        """
        Fetch historical dividend data for the specified company.
        
        :return: List of historical annual dividend values.
        """
        logging.info(f"Fetching dividend history for {self.company}...")
        ticker = Ticker(self.company)
        
        # Get dividend history for the last 5 years of monthly data
        dividend_data = ticker.history(period="5y")

        # Reset the index and ensure 'date' is in UTC to handle tz conflicts
        dividend_data = dividend_data.reset_index()
        dividend_data['date'] = pd.to_datetime(dividend_data['date'], errors='coerce', utc=True)
        
        # Filter only rows with dividend payments and calculate annual dividends
        if 'dividends' in dividend_data.columns:
            dividend_data = dividend_data[dividend_data['dividends'] > 0]
            dividend_data['Year'] = dividend_data['date'].dt.year
            annual_dividends = dividend_data.groupby('Year')['dividends'].sum().tolist()
            return annual_dividends
        else:
            logging.error("No dividend data found.")
            return []

