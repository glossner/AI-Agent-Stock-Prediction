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

    def calculate_growth(self, dividends):
        growth = []
        for i in range(1, len(dividends)):
            growth.append((dividends[i] - dividends[i-1]) / dividends[i-1] * 100)
        return growth

    def backtest(self):
        historical_dividends = self.fetch_dividend_history()
        actual_growth = self.calculate_growth(historical_dividends)

        if len(self.forecasted_growth) > len(actual_growth):
            self.forecasted_growth = self.forecasted_growth[:len(actual_growth)]
        elif len(actual_growth) > len(self.forecasted_growth):
            actual_growth = actual_growth[:len(self.forecasted_growth)]

        mse = mean_squared_error(actual_growth, self.forecasted_growth)
        mape = mean_absolute_percentage_error(actual_growth, self.forecasted_growth)
        mean_error = np.mean(np.abs(np.array(self.forecasted_growth) - np.array(actual_growth)))
        correlation = np.corrcoef(self.forecasted_growth, actual_growth)[0, 1]
        ss_total = sum((np.array(actual_growth) - np.mean(actual_growth))**2)
        ss_residual = sum((np.array(actual_growth) - np.array(self.forecasted_growth))**2)
        r_squared = 1 - (ss_residual / ss_total)

        logging.info(f"Backtest Performance for {self.company}:")
        logging.info(f"Mean Forecast Error: {mean_error:.4f}")
        logging.info(f"Mean Squared Error (MSE): {mse:.4f}")
        logging.info(f"Mean Absolute Percentage Error (MAPE): {mape:.4f}")
        logging.info(f"Correlation: {correlation:.4f}")
        logging.info(f"R-Squared: {r_squared:.4f}")

        return {
            "Forecasted Growth": self.forecasted_growth,
            "Actual Growth": actual_growth,
            "Performance Metrics": {
                "Mean Forecast Error": mean_error,
                "Mean Squared Error": mse,
                "Mean Absolute Percentage Error (MAPE)": mape,
                "Correlation": correlation,
                "R-Squared": r_squared
            }
        }


if __name__ == "__main__":
    company = 'AAPL'
    forecasted_growth = [5, 5, 5, 5, 5]

    backtester = DividendBacktester(company, forecasted_growth=forecasted_growth)
    result = backtester.backtest()
    
    print("\n\n=========================")
    print(f"Dividend Growth Backtest for {company}")
    print("=========================")
    for metric, value in result["Performance Metrics"].items():
        print(f"{metric}: {value:.4f}")