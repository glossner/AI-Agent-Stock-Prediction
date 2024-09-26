import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Indicators.calculate_correlations import CorrelationTool


class InvestmentDecisionAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(
            role='Investment Advisor',
            goal="""Provide investment recommendations based on correlation analysis and market insights.""",
            backstory="""You are a seasoned investment advisor, offering advice on pairs trading opportunities based on correlation and market trends.""",
            verbose=True,
            tools=[],  # Can include tools for further analysis if needed
            **kwargs)

    def investment_decision(self, agent, stock1, stock2):
        return crewai.Task(
            description=dedent(f"""
                Based on the correlation analysis between {stock1} and {stock2}, provide an investment decision.
                Consider market trends, risk factors, and the potential for profit in pairs trading with these stocks.
            """),
            agent=agent,
            expected_output="A detailed investment decision report, including buy/sell recommendations."
        )



