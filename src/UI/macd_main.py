import os
import sys
from crewai import Crew
from textwrap import dedent
from dotenv import load_dotenv

# Import necessary classes from your project
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents  # Agents definition
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks  # Tasks for CrewAI

from src.Indicators.macd import MACDIndicator  # MACD indicator class
from src.Agents.MACD.macd_analysis_agent import MACDAnalysisAgent  # MACD analysis agent
from src.Data_Retrieval.data_fetcher import DataFetcher  # For fetching stock data

# Load environment variables
load_dotenv()

class FinancialCrew:
    def __init__(self, company, stock_data):
        self.company = company
        self.stock_data = stock_data

    def run(self):
        # Initialize agents and tasks
        agents = StockAnalysisAgents()
        tasks = StockAnalysisTasks()

        # Initialize agents
        research_analyst_agent = agents.research_analyst()
        financial_analyst_agent = agents.financial_analyst()
        investment_advisor_agent = agents.investment_advisor()
        
        # Initialize MACD Analysis Agent
        macd_agent = MACDAnalysisAgent().macd_trading_advisor()

        # Create tasks
        research_task = tasks.research(research_analyst_agent, self.company)
        financial_task = tasks.financial_analysis(financial_analyst_agent)
        filings_task = tasks.filings_analysis(financial_analyst_agent)
        recommend_task = tasks.recommend(investment_advisor_agent)

        # MACD Calculation
        macd = MACDIndicator(self.stock_data)
        macd_data = macd.calculate_macd()

        # Create a new task for MACD analysis and pass the report to the MACD analysis agent
        macd_task = MACDAnalysisAgent().macd_analysis(macd_agent, macd_data)

        # Kickoff CrewAI agents and tasks
        crew = Crew(
            agents=[
                research_analyst_agent,
                financial_analyst_agent,
                investment_advisor_agent,
                macd_agent  # Include MACD agent
            ],
            tasks=[
                macd_task,  # Include the MACD task
            ],
            verbose=True
        )

        result = crew.kickoff()
        return result


if __name__ == "__main__":
    print("## Welcome to Financial Analysis Crew")
    print('-------------------------------')

    # Prompt user for company name
    company = input(dedent("""
        What is the company you want to analyze?
    """))

    # Fetch stock data using DataFetcher
    data_fetcher = DataFetcher()
    stock_data = data_fetcher.get_stock_data(company)

    if stock_data.empty:
        print(f"No data found for {company}. Please try again.")
    else:
        # Create FinancialCrew instance
        financial_crew = FinancialCrew(company, stock_data)

        # Run the analysis and display the result
        result = financial_crew.run()

        print("\n\n########################")
        print("## Here is the Report")
        print("########################\n")
        print(result)
