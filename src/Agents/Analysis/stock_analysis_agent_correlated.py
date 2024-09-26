from crewai import Agent
from src.Indicators.calculate_correlations import CorrelationTool  # Import the correlation tool

class StockAnalysisAgents:
    def correlation_analyst(self):
        # Initialize the tool(s) required for the correlation analysis
        correlation_tool = CorrelationTool()

        return Agent(
            role='Stock Correlation Analyst',
            goal="""Analyze the correlation between two specified stocks using historical data.""",
            backstory="""You are a market analyst specialized in identifying highly correlated stocks for potential pairs trading opportunities.""",
            verbose=True,
            tools=[correlation_tool]  # Ensure you pass the tool object, not just its name
        )

    def investment_advisor(self):
        return Agent(
            role='Investment Advisor',
            goal="""Provide investment recommendations based on correlation analysis and market insights.""",
            backstory="""You are a seasoned investment advisor, offering advice on pairs trading opportunities based on correlation and market trends.""",
            verbose=True,
            tools=[]  # Can include tools for further analysis if needed
        )
