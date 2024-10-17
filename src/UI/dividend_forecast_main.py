import os
import sys
from textwrap import dedent
from yahooquery import Ticker
from dotenv import load_dotenv

# Import CrewAI components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from crewai import Crew
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks

# Load environment variables (e.g., API keys)
load_dotenv()

class FinancialCrew:
    def __init__(self, company):
        self.company = company

    def run(self):
        agents = StockAnalysisAgents()
        tasks = StockAnalysisTasks()

        # Create the dividend forecasting agent with the company name
        dividend_forecasting_agent = agents.dividend_forecasting_agent(self.company)

        # Fetch financial data for the company using yahooquery
        financial_data = self.fetch_financial_data()

        # Create the dividend forecasting task with the company name
        dividend_forecasting_task = tasks.forecast_dividend_growth(dividend_forecasting_agent, financial_data, self.company)

        # Kickoff the CrewAI with the agent and task
        crew = Crew(
            agents=[dividend_forecasting_agent],
            tasks=[dividend_forecasting_task],
            verbose=True
        )

        result = crew.kickoff()
        return result

    def fetch_financial_data(self):
        # Fetch financial data using yahooquery
        print(f"Fetching financial data for {self.company}...")
        ticker = Ticker(self.company)
        income_statement = ticker.income_statement(frequency='a')  # Get annual income statement
        cash_flow_statement = ticker.cash_flow(frequency='a')  # Get annual cash flow statement

        # Convert data to strings for easier analysis
        return {
            "IncomeStatement": income_statement.to_string(),
            "CashFlowStatement": cash_flow_statement.to_string()
        }


if __name__ == "__main__":
    print("## Welcome to Dividend Forecasting System")
    print('-------------------------------')

    # Prompt user for company name
    company = input(dedent("""
        What is the company you want to analyze?
    """))

    # Initialize and run the financial crew for the company
    financial_crew = FinancialCrew(company)
    result = financial_crew.run()

    # Print the final result
    print("\n\n########################")
    print("## Dividend Forecasting Report")
    print("########################\n")
    print(result)
