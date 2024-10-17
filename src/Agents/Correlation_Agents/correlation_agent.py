import json
import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Data_Retrieval.data_fetcher import DataFetcher
import logging

class CorrelationAgent(BaseAgent):
    def __init__(self, stock1:str="AAPL", stock2:str="MSFT", **kwargs):
        super().__init__(
            role='Stock Correlation Analyst',
            goal="""Analyze the correlation between two specified stocks using historical data.""",
            backstory="""You are a market analyst specialized in identifying highly correlated stocks for potential pairs trading opportunities.""",
            verbose=True,
            tools=[], 
            allow_delegation = False,
            **kwargs)
        self.stock1 = stock1
        self.stock2 = stock2
        logging.info("CorrelationAgent initialized") 


    def calculate_correlation(self) -> crewai.Task:        
        fetcher = DataFetcher()
        stock1_data = fetcher.get_stock_data(self.stock1)
        print(stock1_data)
        stock2_data = fetcher.get_stock_data(self.stock2)
        logging.info(f"""Data retrieved for {self.stock1} and {self.stock2}  """)
        correlation_coef = stock1_data['Close'].corr(stock2_data['Close'])
        logging.info(f"""Correlaton coefficient is {correlation_coef}""")
        return crewai.Task(
            description=dedent(f"""
                Analyze the historical price data of {self.stock1} and {self.stock2} to calculate their correlation.
                Based on the correlation results, determine if the stocks are suitable for pairs trading.
            """),
            agent=self,
            expected_output = f"The correlation between {self.stock1} and {self.stock2} is: {correlation_coef:.4f}"

        )



