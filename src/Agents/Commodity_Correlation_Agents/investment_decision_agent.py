import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
import logging

class InvestmentDecisionAgent(BaseAgent):
    def __init__(self, stock="AAPL", commodity="OIL", **kwargs):
        super().__init__(
            role='Investment Advisor',
            goal="Provide investment recommendations based on stock-commodity correlation analysis.",
            backstory="You are a seasoned investment advisor offering advice based on commodity impacts on stock prices.",
            verbose=True,
            tools=[], 
            allow_delegation=False,
            **kwargs
        )
        self.stock = stock
        self.commodity = commodity
        logging.info("InvestmentDecisionAgent initialized")

    def investment_decision(self):
        logging.info("investment_decision CrewAI Task being assembled")
        return crewai.Task(
            description=dedent(f"""
                Based on the correlation analysis between {self.stock} and {self.commodity}, provide an investment decision.
                Consider market trends, risk factors, and the influence of commodity price movements on the stock.
            """),
            agent=self,
            expected_output="A detailed investment decision report, including buy/sell recommendations."
        )
