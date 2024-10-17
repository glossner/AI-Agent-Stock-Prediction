import sys
import json
import crewai as crewai
import openai
import crewai_tools as crewai_tools
from src.Data_Retrieval.data_fetcher import DataFetcher
from src.Agents.Trend_Following_Agents.trend_following_agent import TrendFollowingAgent
from textwrap import dedent


# Todo: Add next agent


class TrendCrew:
  def __init__(self, symbol):
      self.is_init = True

  def run(self):
    trend_following_agent = TrendFollowingAgent(symbol)
 
    crew = crewai.Crew(
      agents=[
        trend_following_agent,
      ],
      tasks=[         
        trend_following_agent.find_trend()
      ],
      process=crewai.Process.sequential,
      verbose=True
    )

    result = crew.kickoff()
    return result


    

if __name__ == "__main__":
    print("## Trend Following System")
    print('-------------------------------')
  
  # Input field to choose stock symbol
    symbol = input(
        dedent("""
            What is the company you want to analyze?
            """))
    # Initialize the DataFetcher and retrieve the data
    data_fetcher = DataFetcher()
    data = data_fetcher.get_stock_data(symbol)



    trend_crew = TrendCrew(symbol)
    crew_output = trend_crew.run()
    
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

