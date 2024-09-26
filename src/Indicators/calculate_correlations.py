import yfinance as yf
import pandas as pd
from pydantic import BaseModel, Field
from langchain.tools import tool

# class CorrelationToolSchema(BaseModel):
#     stock_1: str = Field(..., description="Ticker symbol of the first stock.")
#     stock_2: str = Field(..., description="Ticker symbol of the second stock.")
#     start_date: str = Field('2020-01-01', description="Start date for historical data in the format 'YYYY-MM-DD'.")
#     end_date: str = Field('2023-01-01', description="End date for historical data in the format 'YYYY-MM-DD'.")

class CorrelationTool:
    name = "Calculate stock correlation"
    #args_schema = CorrelationToolSchema  # Adding args_schema for the tool

    @tool("Calculate stock correlation")
    def calculate_correlation(self, stock_1: str, stock_2: str, start_date: str = '2020-01-01', end_date: str = '2023-01-01'):
        """
        Calculate the correlation between two specified stocks over a given date range.
        """
        try:
            # Fetch stock data using yfinance
            data_1 = yf.download(stock_1, start=start_date, end=end_date)['Close']
            data_2 = yf.download(stock_2, start=start_date, end=end_date)['Close']
            
            # Combine the data into a DataFrame
            df = pd.DataFrame({stock_1: data_1, stock_2: data_2})
            
            # Calculate the correlation
            correlation = df[stock_1].corr(df[stock_2])
            
            return f"The correlation between {stock_1} and {stock_2} is: {correlation:.4f}"
        
        except Exception as e:
            return f"An error occurred while calculating correlation: {str(e)}"