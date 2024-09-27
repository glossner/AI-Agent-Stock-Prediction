import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
import logging

class InvestmentDecisionAgent(BaseAgent):
    def __init__(self, stock1="AAPL", stock2="MSFT", **kwargs):
        super().__init__(
            role='Investment Advisor',
            goal="""Provide investment recommendations based on correlation analysis and market insights.""",
            backstory="""You are a seasoned investment advisor, offering advice on pairs trading opportunities based on correlation and market trends.""",
            verbose=True,
            tools=[],  # Can include tools for further analysis if needed
            allow_delegation = False,
            **kwargs)
        self.stock1 = stock1
        self.stock2 = stock2
        logging.info("InvestmentDecisionAgent initialized")

    def investment_decision(self):       
        logging.info("investment_decision CrewAI Task being assembled") 
        return crewai.Task(
            description=dedent(f"""
                Based on the correlation analysis between {self.stock1} and {self.stock2}, provide an investment decision.
                Consider market trends, risk factors, and the potential for profit in pairs trading with these stocks.
            """),
            agent=self,
            expected_output="A detailed investment decision report, including buy/sell recommendations."
        )



