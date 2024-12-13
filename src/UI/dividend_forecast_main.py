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
import langchain_openai as lang_oai


# Load environment variables (e.g., API keys)
load_dotenv()

gpt_4o_high_tokens = lang_oai.ChatOpenAI(
    model_name="gpt-4o",
    temperature=0.0,
    max_tokens=1500
)

class FinancialCrew:
    def __init__(self, company):
        self.company = company

    def run(self):
        agents = StockAnalysisAgents(gpt_model=gpt_4o_high_tokens)
        tasks = StockAnalysisTasks()

        # Create the dividend forecasting agent with the company name
        research_agent = agents.research_analyst()
        financial_analysis_agent = agents.financial_analyst()
        dividend_forecasting_agent = agents.dividend_forecasting_agent(self.company)

        # Fetch financial data for the company using yahooquery
        financial_data = self.fetch_financial_data()

        # Create the dividend forecasting task with the company name
        research_task = tasks.research(research_agent, self.company)
        financial_filings_task = tasks.filings_analysis(financial_analysis_agent)
        financial_analysis_task = tasks.financial_analysis(financial_analysis_agent)
        dividend_forecasting_task = tasks.forecast_dividend_growth(dividend_forecasting_agent, financial_data, self.company)

        # Kickoff the CrewAI with the agent and task
        crew = Crew(
            agents=[research_agent, dividend_forecasting_agent],
            tasks=[research_task, financial_filings_task, financial_analysis_task, dividend_forecasting_task],
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
