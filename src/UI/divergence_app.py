######################################
# This code implements divergence detection and analysis using CrewAI
######################################
#
# The following keys must be defined in the environment shell
# OPENAI_API_KEY=sk-
# SEC_API_API_KEY=
# SERPER_API_KEY
#
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from crewai import Crew
from textwrap import dedent

from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks
from src.Agents.divergence_agents.divergence_agent import DivergenceAnalysisAgents, DivergenceAnalysisTasks  # Updated import
from src.Data_Retrieval.data_fetcher import DataFetcher
from src.Indicators.rsi_divergence import RSIIndicator
from src.Indicators.macd_indicator import MACDIndicator
from dotenv import load_dotenv
load_dotenv()

class FinancialCrew:
    def __init__(self, company, indicator_name):
        self.company = company
        self.indicator_name = indicator_name

    def run(self):
        # Initialize agents and tasks
        agents = StockAnalysisAgents()
        divergence_agents = DivergenceAnalysisAgents()  # Create an instance of DivergenceAnalysisAgents
        tasks = StockAnalysisTasks()
        divergence_tasks = DivergenceAnalysisTasks()

        # Initialize the divergence trading advisor agent
        divergence_agent = divergence_agents.divergence_trading_advisor()  # Use the instance to call the method

        # Fetch stock data
        data_fetcher = DataFetcher()
        stock_data = data_fetcher.get_stock_data(self.company)

        # Calculate MACD or RSI data
        if self.indicator_name == 'MACD':
            indicator_data = MACDIndicator().calculate(stock_data)
        elif self.indicator_name == 'RSI':
            indicator_data = RSIIndicator().calculate(stock_data)

        # Create a divergence detection task
        divergence_task = divergence_tasks.detect_divergence(divergence_agent, stock_data, indicator_data, self.indicator_name)

        # Kickoff CrewAI agents and tasks
        crew = Crew(
            agents=[divergence_agent],
            tasks=[divergence_task],
            verbose=True
        )

        result = crew.kickoff()
        return result

if __name__ == "__main__":
    print("## Welcome to Divergence Trading System")
    print('-------------------------------')

    # Prompt user for company name and indicator (MACD/RSI)
    company = input(dedent("""
        What is the company you want to analyze?
    """))
    indicator_name = input(dedent("""
        Which indicator do you want to use for divergence detection? (MACD/RSI):
    """))

    # Create FinancialCrew instance and run the analysis
    financial_crew = FinancialCrew(company, indicator_name)
    result = financial_crew.run()

    print("\n\n########################")
    print("## Here is the Report")
    print("########################\n")
    print(result)