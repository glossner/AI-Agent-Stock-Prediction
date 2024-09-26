import json
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
            tools=[], 
            **kwargs)

    def calculate_correlation(self, agent, stock1, stock2):
        correlation_tool = CorrelationTool()
        correlation_data = correlation_tool.calculate_correlation(stock1, stock2)
        return crewai.Task(
            description=dedent(f"""
                Analyze the historical price data of {stock1} and {stock2} to calculate their correlation.
                Based on the correlation results, determine if the stocks are suitable for pairs trading.
            """),
            agent=agent,
            #expected_output="A report on the correlation between the two stocks and its significance for investment."
            expected_output=json.dumps(correlation_data)
        )



