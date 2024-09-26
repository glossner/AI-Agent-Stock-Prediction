import os
import sys
import json
import crewai as crewai
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
        crew = crewai.Crew(
            agents=[correlation_agent, investment_decision_agent],
            tasks=[correlation_task, investment_decision_task],
            process=crewai.Process.sequential,
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
    crew_output = correlation_crew.run()

   # Accessing the crew output
    print("\n\n########################")
    print("## Here is the Report")
    print("########################\n")

    print(f"Raw Output: {crew_output.raw}")
    if crew_output.json_dict:
        print(f"\n\nJSON Output: {json.dumps(crew_output.json_dict, indent=2)}")
    if crew_output.pydantic:
        print(f"\n\nPydantic Output: {crew_output.pydantic}")
    
    print(f"\n\nTasks Output: {crew_output.tasks_output}")
    print(f"\n\nToken Usage: {crew_output.token_usage}") 

    print("Collaboraton complete")
    sys.exit(0)  