import os
import sys
from textwrap import dedent
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from crewai import Crew
from src.Agents.VWAP.vwap_analysis_agent import VWAPAnalysisAgent
from src.Indicators.vwap import VWAPIndicator
from src.Data_Retrieval.data_fetcher import DataFetcher

class FinancialCrewVWAP:
    def __init__(self, company):
        self.company = company

    def run(self):
        # Initialize VWAP analysis agent
        vwap_analysis_agent = VWAPAnalysisAgent()
        vwap_agent = vwap_analysis_agent.vwap_trading_advisor()

        # Fetch stock data using DataFetcher
        data_fetcher = DataFetcher()
        stock_data = data_fetcher.get_stock_data(self.company)

        # Flatten MultiIndex columns if present
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = [' '.join(col).strip() for col in stock_data.columns.values]
            # Rename columns to match expected names
            stock_data = stock_data.rename(columns={
                'Adj Close AAPL': 'Adj Close',
                'Close AAPL': 'Close',
                'High AAPL': 'High',
                'Low AAPL': 'Low',
                'Open AAPL': 'Open',
                'Volume AAPL': 'Volume'
            })
        
        # Debug: Check columns after flattening
        print("Columns after flattening and renaming:", stock_data.columns.tolist())

        # Calculate VWAP using the VWAPIndicator
        vwap_indicator = VWAPIndicator()
        vwap_data = vwap_indicator.calculate(stock_data)

        # Create a VWAP analysis task
        vwap_task = vwap_analysis_agent.vwap_analysis(vwap_agent, vwap_data)

        # Run the agents and tasks in the Crew
        crew = Crew(
            agents=[vwap_agent],
            tasks=[vwap_task],
            verbose=True
        )

        result = crew.kickoff()
        return result

if __name__ == "__main__":
    print("## Welcome to VWAP Trading System")
    print('-------------------------------')

    # Prompt user for the company to analyze
    company = input(
        dedent("""What is the company you want to analyze? """))

    # Create FinancialCrewVWAP instance and run the analysis
    financial_crew_vwap = FinancialCrewVWAP(company)
    result = financial_crew_vwap.run()

    print("\n\n########################")
    print("## Here is the Report")
    print("########################\n")
    print(result)
