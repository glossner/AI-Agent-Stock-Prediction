import json
import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Data_Retrieval.data_fetcher_commodity import DataFetcher
import logging

class CommodityCorrelationAgent(BaseAgent):
    def __init__(self, stock: str = "AAPL", commodity: str = "OIL", **kwargs):
        super().__init__(
            role='Commodity Correlation Analyst',
            goal="Analyze the correlation between a specified stock and a commodity using historical data.",
            backstory="You are a market analyst specializing in understanding how commodity prices influence stock performance.",
            verbose=True,
            tools=[], 
            allow_delegation=False,
            **kwargs
        )
        self.stock = stock
        self.commodity = commodity
        logging.info("CommodityCorrelationAgent initialized")

    def calculate_correlation(self) -> crewai.Task:
        fetcher = DataFetcher()
        stock_data = fetcher.get_stock_data(self.stock)
        commodity_data = fetcher.get_commodity_data(self.commodity)
        
        logging.info(f"Data retrieved for {self.stock} and {self.commodity}")
        correlation_coef = stock_data['Close'].corr(commodity_data['Close'])
        
        return crewai.Task(
            description=dedent(f"""
                Analyze the historical price data of {self.stock} and {self.commodity} to calculate their correlation.
                Based on the correlation results, determine how the commodity influences stock performance.
            """),
            agent=self,
            expected_output=f"The correlation between {self.stock} and {self.commodity} is: {correlation_coef:.4f}"
        )
