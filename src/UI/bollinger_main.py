import os
import sys
from crewai import Crew
from textwrap import dedent
from dotenv import load_dotenv
from src.Agents.Bollinger_agent.bollinger_agent import BollingerAnalysisAgents
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Indicators.bollinger import BollingerBands  # Import BollingerBands class
from src.Data_Retrieval.data_fetcher import DataFetcher  # Import DataFetcher class

# Load environment variables
load_dotenv()

class FinancialCrew:
    def __init__(self, company, stock_data):
        self.company = company
        self.stock_data = stock_data

    def run(self):
        # Initialize agents
        stock_analysis_agents = StockAnalysisAgents()
        bollinger_agents = BollingerAnalysisAgents()
        
        # Initialize agents
        research_analyst_agent = stock_analysis_agents.research_analyst()
        financial_analyst_agent = stock_analysis_agents.financial_analyst()
        investment_advisor_agent = stock_analysis_agents.investment_advisor()
        bollinger_agent = bollinger_agents.bollinger_bands_investment_advisor()

        # Bollinger Bands Calculation
        bollinger = BollingerBands(self.stock_data)
        bollinger_bands = bollinger.calculate_bands()

        # Create tasks for Bollinger Bands analysis
        bollinger_task1 = bollinger_agents.bollinger_analysis(research_analyst_agent, bollinger_bands)
        bollinger_task2 = bollinger_agents.bollinger_analysis(financial_analyst_agent, bollinger_bands)
        bollinger_task3 = bollinger_agents.bollinger_analysis(investment_advisor_agent, bollinger_bands)
        bollinger_task4 = bollinger_agents.bollinger_analysis(bollinger_agent, bollinger_bands)

        # Kickoff CrewAI agents and tasks
        crew = Crew(
            agents=[
                research_analyst_agent,
                financial_analyst_agent,
                investment_advisor_agent,
                bollinger_agent
            ],
            tasks=[
                bollinger_task1,
                bollinger_task2,
                bollinger_task3,
                bollinger_task4  # Include the Bollinger Bands analysis task
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
