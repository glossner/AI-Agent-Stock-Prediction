from dotenv import load_dotenv
import os
load_dotenv()
for key, value in os.environ.items():
    print(f"{key}: {value}")


import sys
import json
import crewai as crewai
import openai
import crewai_tools as crewai_tools
from src.Agents.Scenario_Agents.portfolio_data_agent import PortfolioDataAgent
from src.Agents.Scenario_Agents.scenario_input_agent import ScenarioInputAgent
from src.Agents.Scenario_Agents.scenario_input_critic_agent import ScenarioInputCriticAgent
from src.Agents.Scenario_Agents.scenario_simulation_agent import ScenarioSimulationAgent
from src.Helpers.pretty_print_crewai_output import display_crew_output
from textwrap import dedent
from dotenv import load_dotenv
import logging

# Initialize logger if not already present

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class ScenarioCrew:
  def __init__(self):
      self.is_init = True

  def run(self):
    portfolio_data_agent = PortfolioDataAgent()
    scenario_input_agent = ScenarioInputAgent()
    scenario_input_critic_agent = ScenarioInputCriticAgent()
    

    crew = crewai.Crew(
      agents=[
        portfolio_data_agent,
        scenario_input_agent,
        scenario_input_critic_agent
      ],
      tasks=[
        portfolio_data_agent.retrieve_portfolio_data(),
        scenario_input_agent.get_scenarios_from_news(),
        scenario_input_critic_agent.critique_scenario_input_agent()
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
    logging.info("scenario crew initialized successfully")


    crew_output = scenario_crew.run()
    logging.info("scenario crew execution run() successfully")
    
    # Accessing the crew output
    print("\n\n########################")
    print("## Here is the Report")
    print("########################\n")

    display_crew_output(crew_output)

    print("Collaboraton complete")
    sys.exit(0)  

