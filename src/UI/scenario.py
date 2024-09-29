import sys
import json
import crewai as crewai
import openai
import crewai_tools as crewai_tools
from src.Agents.Scenario_Agents.scenario_input_agent import ScenarioInputAgent
from src.Agents.Scenario_Agents.portfolio_data_agent import PortfolioDataAgent
#from src.Agents.Scenario_Agents.scenario_simulation_agent import ScenarioSimulationAgent
from textwrap import dedent
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ScenarioCrew:
  def __init__(self):
      self.is_init = True

  def run(self):
    scenario_input_agent = ScenarioInputAgent()
    portfolio_data_agent = PortfolioDataAgent()

    crew = crewai.Crew(
      agents=[
        portfolio_data_agent,
        scenario_input_agent       
      ],
      tasks=[
        portfolio_data_agent.retrieve_portfolio_data(),
        scenario_input_agent.get_scenarios_from_news()
      ],
      process=crewai.Process.sequential,
      verbose=True
    )

    result = crew.kickoff()
    return result


    

if __name__ == "__main__":
    print("## Scenario Analysis")
    print('-------------------------------')
  
    scenario_crew = ScenarioCrew()
    crew_output = scenario_crew.run()
    
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

