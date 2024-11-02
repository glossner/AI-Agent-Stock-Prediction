from crewai import Agent
from src.Agents.base_agent import BaseAgent

class VWAPAnalysisAgent(BaseAgent):
    def vwap_trading_advisor(self):
        return Agent(
            role='VWAP Trading Advisor',
            goal="""Analyze VWAP data and provide actionable insights on stock price movement and 
            market momentum based on volume-weighted price. Assist in identifying optimal entry 
            and exit points for trading based on VWAP analysis.""",
            backstory="""This agent specializes in VWAP analysis to assist traders in making decisions 
            based on institutional activity and market sentiment.""",
            verbose=True
        )

    def vwap_analysis(self, agent, vwap_data):
        description = f"""
            Analyze the provided VWAP data, which represents the average price at which a stock 
            has traded throughout the day based on volume. Based on this VWAP data, provide 
            trading recommendations that reflect the current market sentiment. 
            VWAP Data:
            - VWAP: {vwap_data['VWAP'].iloc[-1]}
            - Closing Price: {vwap_data['Close'].iloc[-1]}
        """
        return Task(
            description=description,
            agent=agent,
            expected_output="A report analyzing VWAP data with trading recommendations."
        )
