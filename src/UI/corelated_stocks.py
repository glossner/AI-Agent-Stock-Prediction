import os
import sys
from crewai import Crew
from textwrap import dedent
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import the necessary agents and tasks
#from src.Agents.Analysis.stock_analysis_agent_correlated  import StockAnalysisAgents
#from src.Agents.Analysis.stock_analysis_task_correlated import StockAnalysisTasks
from src.Agents.Correlation_Agents.correlation_agent import CorrelationAgent
from src.Agents.Correlation_Agents.investment_decision_agent import InvestmentDecisionAgent

load_dotenv()

class StockCorrelationCrew:
    def __init__(self, stock1="AAPL", stock2="MSFT"):
        self.stock1 = stock1
        self.stock2 = stock2

    def run(self):
        #agents = StockAnalysisAgents()
        #tasks = StockAnalysisTasks()

        # Initialize agents        
        correlation_agent = CorrelationAgent()
        investment_decision_agent = InvestmentDecisionAgent()
        #investment_advisor_agent = agents.investment_advisor()

        # Initialize tasks
        correlation_task = correlation_agent.calculate_correlation
        investment_decision_task = investment_decision_agent.investment_decision
        #correlation_task = tasks.calculate_correlation(correlation_agent, self.stock1, self.stock2)
        #investment_task = tasks.investment_decision(investment_advisor_agent, self.stock1, self.stock2)

        # Use Crew to coordinate agents and tasks
        crew = Crew(
            agents=[correlation_agent, investment_decision_agent],
            tasks=[correlation_task, investment_decision_task],
            verbose=True
        )

        # Kickoff the analysis and return the result
        result = crew.kickoff()
        return result

if __name__ == "__main__":
    print("## Stock Correlation and Investment Analysis ##")
    stock1 = input("Enter the first stock ticker: ")
    stock2 = input("Enter the second stock ticker: ")

    # Initialize the correlation crew with the two stock tickers
    correlation_crew = StockCorrelationCrew(stock1, stock2)
    result = correlation_crew.run()

    print("\n\n########################")
    print("## Investment Analysis Report ##")
    print("########################\n")
    print(result)
