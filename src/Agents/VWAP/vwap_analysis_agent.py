from crewai import Agent
from src.Agents.base_agent import BaseAgent
from textwrap import dedent
from crewai import Task

class VWAPAnalysisAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(
            role='VWAP Trading Advisor',
            goal="Analyze VWAP data to provide trading insights based on market momentum and institutional investor activity.",
            backstory="You are an expert market analyst specializing in VWAP analysis, helping traders make decisions based on institutional activity and market momentum.",
            verbose=True,
            tools=[], 
            allow_delegation=False,
            **kwargs
        )
    
    def vwap_trading_advisor(self):
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            verbose=self.verbose,
            tools=self.tools,
            allow_delegation=self.allow_delegation
        )

    def vwap_analysis(self, agent, vwap_data):
        description = dedent(f"""
            Analyze the provided VWAP data, which represents the average price at which a stock 
            has traded throughout the day based on volume. Provide trading recommendations 
            reflecting the current market sentiment. 
            VWAP Data:
            - VWAP: {vwap_data['VWAP'].iloc[-1]}
            - Closing Price: {vwap_data['Close'].iloc[-1]}
        """)
        return Task(
            description=description,
            agent=agent,
            expected_output="A report analyzing VWAP data with trading recommendations."
        )
