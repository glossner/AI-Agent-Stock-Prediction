
import re
from pydantic import BaseModel, Field
from src.Agents.base_agent import BaseAgent


class ScenarioInputAgent(BaseAgent):
    # Define scenario_patterns as a class-level attribute using Field with a default_factory
    scenario_patterns: dict = Field(default_factory=lambda: {
        'interest_rate': re.compile(r'interest rates (rise|fall) by (\d+\.?\d*)%'),
        'oil_price': re.compile(r'oil prices (increase|decrease) by (\d+\.?\d*)%'),
        'stock_price': re.compile(r'stock prices (rise|fall) by (\d+\.?\d*)%'),
        'inflation': re.compile(r'inflation (increases|decreases) by (\d+\.?\d*)%'),
    })

    def __init__(self, **kwargs):
        super().__init__(
            role='Scenario Input Agent',
            goal='Interpret and handle market scenarios',
            backstory='Handles market scenario inputs for financial simulations.',
            **kwargs)
 
    # Subtask 1: Interpret natural language input
    def interpret_input(self, user_input):
        """
        Handles natural language inputs and interprets them into a structured format.
        """
        structured_data = {}

        # Loop over scenario patterns and extract relevant data
        for scenario, pattern in self.scenario_patterns.items():
            match = pattern.search(user_input)
            if match:
                structured_data[scenario] = {
                    'action': match.group(1),  # rise/fall/increase/decrease
                    'value': float(match.group(2))  # percentage value
                }
        return structured_data

    # Subtask 2: Flexibility to handle various scenarios
    def handle_flexible_scenarios(self, user_input):
        """
        Ensures flexibility in handling different types of market scenarios by identifying
        variables like interest rates, oil prices, or stock market fluctuations.
        """
        # Extract structured data from input
        structured_data = self.interpret_input(user_input)

        if not structured_data:
            return "No valid market scenario detected. Please check your input."

        return structured_data

    # Subtask 3: Validate the input
    def validate_input(self, structured_data):
        """
        Validates the input to ensure the query is correct and meaningful.
        """
        valid_scenarios = ['interest_rate', 'oil_price', 'stock_price', 'inflation']

        # Check if the extracted data corresponds to known valid scenarios
        for scenario in structured_data.keys():
            if scenario not in valid_scenarios:
                return False, f"Invalid scenario detected: {scenario}"

        return True, "Valid scenario input."

    # Subtask 4: Collaborate with Scenario Simulation Agent
    def collaborate_with_simulation_agent(self, structured_data):
        """
        Passes structured data to the Scenario Simulation Agent for further processing.
        """
        # Simulating a call to the Scenario Simulation Agent
        print("Passing the following data to the Scenario Simulation Agent:")
        print(structured_data)
        # In a real implementation, this would be where the Scenario Simulation Agent is invoked
        return True