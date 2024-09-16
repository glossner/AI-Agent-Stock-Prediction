import sys
import crewai as crewai
import openai
import crewai_tools as crewai_tools
from src.Agents.Scenario_Agents.scenario_input_agent import ScenarioInputAgent
#from src.Agents.Analysis.Tools.search_tools import SearchTools





# Example usage:
if __name__ == "__main__":
    # Initialize the Scenario Input Agent
    agent = ScenarioInputAgent()

    # Example input
    user_input = "What happens if interest rates rise by 1.5%?"

    # Handle input and extract structured data
    structured_data = agent.handle_flexible_scenarios(user_input)
    
    # Validate the structured data
    is_valid, message = agent.validate_input(structured_data)
    
    if is_valid:
        # Collaborate with the Scenario Simulation Agent if valid
        agent.collaborate_with_simulation_agent(structured_data)
        print("Collaboraton complete")
    else:
        print(f"Validation failed: {message}")

    sys.exit(0)    

