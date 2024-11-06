import os
import crewai as crewai
from textwrap import dedent
import logging
from src.Agents.Commodity_Correlation_Agents.commodity_correlation_agent import CommodityCorrelationAgent
from src.Agents.Commodity_Correlation_Agents.investment_decision_agent import InvestmentDecisionAgent
from src.Helpers.pretty_print_crewai_output import display_crew_output

logging.basicConfig(level=logging.INFO)

class CommodityCorrelationCrew:
    def __init__(self, stock="AAPL", commodity="OIL"):
        self.stock = stock
        self.commodity = commodity

    def run(self):
        correlation_agent = CommodityCorrelationAgent(self.stock, self.commodity)
        investment_decision_agent = InvestmentDecisionAgent(self.stock, self.commodity)

        crew = crewai.Crew(
            agents=[correlation_agent, investment_decision_agent],
            tasks=[correlation_agent.calculate_correlation(), investment_decision_agent.investment_decision()],
            process=crewai.Process.sequential,
            verbose=True
        )

        logging.info("CrewAI crew created for commodity correlation analysis")
        result = crew.kickoff()
        return result

if __name__ == "__main__":
    stock = input("Enter the stock ticker: ")
    commodity = input("Enter the commodity (e.g., 'OIL' or 'GOLD'): ")

    correlation_crew = CommodityCorrelationCrew(stock, commodity)
    crew_output = correlation_crew.run()
    display_crew_output(crew_output)
