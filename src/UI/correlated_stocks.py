import os
import sys
import json
import crewai as crewai
from textwrap import dedent
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from dotenv import load_dotenv
import logging
from src.Agents.Correlation_Agents.correlation_agent import CorrelationAgent
from src.Agents.Correlation_Agents.investment_decision_agent import InvestmentDecisionAgent
from src.Helpers.pretty_print_crewai_output import display_crew_output

load_dotenv()

logging.basicConfig(level=logging.INFO)


class StockCorrelationCrew:
    def __init__(self, stock1="AAPL", stock2="MSFT"):
        self.stock1 = stock1
        self.stock2 = stock2

    def run(self):
        # Initialize agents        
        correlation_agent = CorrelationAgent(self.stock1, self.stock2)
        investment_decision_agent = InvestmentDecisionAgent(self.stock1, self.stock2)
        
        logging.info("Correlation and Investment Decision agents initialized")
        
        # Use Crew to coordinate agents and tasks
        crew = crewai.Crew(
            agents=[
                correlation_agent, 
                investment_decision_agent
            ],
            tasks=[
                correlation_agent.calculate_correlation(), 
                investment_decision_agent.investment_decision()
            ],
            process=crewai.Process.sequential,
            verbose=True
        )

        logging.info("CrewAI crew created")
        result = crew.kickoff()
        return result



if __name__ == "__main__":
    print("## Stock Correlation and Investment Analysis ##")
    stock1 = input("Enter the first stock ticker: ")
    stock2 = input("Enter the second stock ticker: ")

    logging.info(f"""The two stocks are {stock1} and {stock2}""")

    # Initialize the correlation crew with the two stock tickers
    correlation_crew = StockCorrelationCrew(stock1, stock2)
    crew_output = correlation_crew.run()

   # Accessing the crew output
    print("\n\n########################")
    print("## Here is the Report")
    print("########################\n")

    display_crew_output(crew_output)

    print("Collaboraton complete")
    sys.exit(0)  