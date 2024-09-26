#from crewai import Agent
import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Indicators.calculate_correlations import CorrelationTool


class CorrelationAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(
             role='Stock Correlation Analyst',
            goal="""Analyze the correlation between two specified stocks using historical data.""",
            backstory="""You are a market analyst specialized in identifying highly correlated stocks for potential pairs trading opportunities.""",
            verbose=True,
            tools=[CorrelationTool.calculate_correlation], 
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




# class StockAnalysisAgents:
#     def correlation_analyst(self):
#         # Initialize the tool(s) required for the correlation analysis
#         correlation_tool = CorrelationTool()

#         return Agent(
#             role='Stock Correlation Analyst',
#             goal="""Analyze the correlation between two specified stocks using historical data.""",
#             backstory="""You are a market analyst specialized in identifying highly correlated stocks for potential pairs trading opportunities.""",
#             verbose=True,
#             tools=[correlation_tool]  # Ensure you pass the tool object, not just its name
#         )

#     def investment_advisor(self):
#         return Agent(
#             role='Investment Advisor',
#             goal="""Provide investment recommendations based on correlation analysis and market insights.""",
#             backstory="""You are a seasoned investment advisor, offering advice on pairs trading opportunities based on correlation and market trends.""",
#             verbose=True,
#             tools=[]  # Can include tools for further analysis if needed
#         )
