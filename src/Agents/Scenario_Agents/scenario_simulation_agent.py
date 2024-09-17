from src.Agents.base_agent import BaseAgent
from pydantic import PrivateAttr


class ScenarioSimulationAgent(BaseAgent):
    _scenario_data: dict = PrivateAttr()
    _portfolio_data: dict = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(
            role='Scenario Simulation Agent',
            goal='Simulate market scenarios on portfolio data',
            backstory='Simulates the impact of market scenarios on the portfolio.',
            **kwargs)
        self._scenario_data = None
        self._portfolio_data = None

    def on_receive(self, sender, message):
        if sender == 'ScenarioInputAgent':
            self._scenario_data = message
            self.logger.info(f"Received scenario data from {sender}")
        elif sender == 'PortfolioDataAgent':
            self._portfolio_data = message
            self.logger.info(f"Received portfolio data from {sender}")

        if self._scenario_data and self._portfolio_data:
            self.run_simulation()

    def run_simulation(self):
        # Simulate the scenario impact on the portfolio
        self.logger.info("Running simulation with the following data:")
        self.logger.info(f"Scenario Data: {self._scenario_data}")
        self.logger.info(f"Portfolio Data: {self._portfolio_data}")
        # Placeholder for simulation logic
        self.logger.info("Simulation complete.")
        # Reset data after simulation
        self._scenario_data = None
        self._portfolio_data = None