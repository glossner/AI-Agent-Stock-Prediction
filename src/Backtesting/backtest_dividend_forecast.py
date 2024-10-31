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