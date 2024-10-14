from src.Agents.base_agent import BaseAgent
import crewai as crewai
from pydantic import PrivateAttr
from textwrap import dedent


class ScenarioSimulationAgent(BaseAgent):
    _scenario_data: dict = PrivateAttr()
    _portfolio_data: dict = PrivateAttr()


    def __init__(self, **kwargs):
        super().__init__(
            role='Scenario Simulation Agent',
            goal=dedent("""
                Provide the likely impact of market scenarios on ticker data.
            """),
            backstory='Simulates the impact of market scenarios on the portfolio.',
            **kwargs)
 
    def run_simulation(self):
        return crewai.Task(
            description=dedent(f"""
             Based on the Scenario Input Agent's report, simulate the likely range of 
                        impacts on the portfolio tickers.            
            After computing the range based on the Scenario Input Agent's report, consider
                        the impact due natural disasters like hurricanes or floods, 
                        terrorist attacks, GDP or inflation changes.
            Summarize it as 2 parts: 
                        1) Scenario Input Agent's likely change and
                        2) Likelyhood of disasters and range of impacts          
            """),
            agent=self,
            expected_output=dedent("""
                A table with rows organized by portfolio ticker and 
                columns organized in two sections: Scenario Agent's likely min/max changes and
                Disaster min/max changes with a likelihood of the disaster.
                """)
        )


