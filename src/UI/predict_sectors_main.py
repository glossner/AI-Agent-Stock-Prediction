import os
import sys
from textwrap import dedent
from fredapi import Fred
from dotenv import load_dotenv

# Import CrewAI components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from crewai import Crew
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks

# Load environment variables (e.g., API keys)
load_dotenv()

class EconomicCrew:
    def __init__(self):
        self.fred_api_key = os.getenv('FRED_API_KEY')
        self.fred = Fred(api_key=self.fred_api_key)

    def run(self):
        agents = StockAnalysisAgents()
        tasks = StockAnalysisTasks()

        # Create the economic forecasting agent
        economic_forecasting_agent = agents.economic_forecasting_agent()

        # Fetch macroeconomic data
        macroeconomic_data = self.fetch_macroeconomic_data()

        # Combine with financial reports and policy changes (assume you have these from external sources)
        combined_data = self.get_combined_data(macroeconomic_data)

        # Create the sector prediction task
        sector_prediction_task = tasks.predict_sector_performance(economic_forecasting_agent, combined_data)

        # Kickoff the CrewAI with the agent and task
        crew = Crew(
            agents=[economic_forecasting_agent],
            tasks=[sector_prediction_task],
            verbose=True
        )

        result = crew.kickoff()
        return result

    def fetch_macroeconomic_data(self):
        # Example: Fetch unemployment rate, GDP, and inflation data from FRED
        print("Fetching macroeconomic data from FRED...")

        gdp = self.fred.get_series('GDP')  # GDP
        inflation = self.fred.get_series('CPIAUCSL')  # Consumer Price Index for All Urban Consumers
        unemployment = self.fred.get_series('UNRATE')  # Unemployment Rate

        return {
            "GDP": gdp.to_string(),
            "Inflation": inflation.to_string(),
            "UnemploymentRate": unemployment.to_string()
        }

    def get_combined_data(self, macroeconomic_data):
        # Add financial reports and government policy changes here
        # For example, fetching the latest financial reports and manually entering policy changes

        # Example: combining macroeconomic data with policy changes (fictitious policy changes for this example)
        financial_reports = "Latest Financial Reports: Report A, Report B, ..."
        policy_changes = "Recent Policy Changes: Policy X, Policy Y, ..."

        combined_data = {
            "MacroeconomicData": macroeconomic_data,
            "FinancialReports": financial_reports,
            "PolicyChanges": policy_changes
        }

        return combined_data


if __name__ == "__main__":
    print("## Welcome to Economic Sector Prediction System")
    print('-------------------------------')

    # Initialize and run the economic crew
    economic_crew = EconomicCrew()
    result = economic_crew.run()

    # Print the final result
    print("\n\n########################")
    print("## Sector Performance Prediction Report")
    print("########################\n")
    print(result)
