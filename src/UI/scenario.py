import sys
import json
import crewai as crewai
import openai
import crewai_tools as crewai_tools
from src.Agents.Scenario_Agents.scenario_input_agent import ScenarioInputAgent
from src.Agents.Scenario_Agents.portfolio_data_agent import PortfolioDataAgent
from src.Agents.Scenario_Agents.scenario_simulation_agent import ScenarioSimulationAgent
#from src.Agents.Analysis.Tools.search_tools import SearchTools


def main():
    # Initialize agents
    scenario_input_agent = ScenarioInputAgent(name='ScenarioInputAgent')
    portfolio_agent = PortfolioDataAgent(name='PortfolioDataAgent')
    simulation_agent = ScenarioSimulationAgent(name='ScenarioSimulationAgent')


   # Register agents with CrewAI's agent manager
    agents = [scenario_input_agent, portfolio_agent, simulation_agent]
    crew = crewai.Crew(agents=agents, verbose=True)


    #Set up the scenario
    portfolio_agent.setup()
    user_input = "What happens if interest rates rise by 1.5%?"

    # Handle input and extract structured data
    structured_data = scenario_input_agent.handle_flexible_scenarios(user_input)
    
    # Validate the structured data
    is_valid, message = scenario_input_agent.validate_input(structured_data)
    
    if is_valid:
        # Collaborate with the Scenario Simulation Agent if valid

        crew_output = crew.kickoff()
        
        # Accessing the crew output
        print(f"Raw Output: {crew_output.raw}")
        if crew_output.json_dict:
            print(f"JSON Output: {json.dumps(crew_output.json_dict, indent=2)}")
        if crew_output.pydantic:
            print(f"Pydantic Output: {crew_output.pydantic}")
        print(f"Tasks Output: {crew_output.tasks_output}")
        print(f"Token Usage: {crew_output.token_usage}") 

        print("Collaboraton complete")
    else:
        print(f"Validation failed: {message}")
    

 
# Example usage:
if __name__ == "__main__":
    main()
    sys.exit(0)  

