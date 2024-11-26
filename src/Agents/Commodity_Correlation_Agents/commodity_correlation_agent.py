import json
import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Data_Retrieval.data_fetcher_commodity import DataFetcher
import logging
import pandas as pd


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

        # Debug to confirm structure
        print("Stock Data Columns:", stock_data.columns)
        print("Commodity Data Columns:", commodity_data.columns)

        # Access the Close columns for stock and commodity
        stock_close = stock_data[f"Close_{self.stock}"]
        commodity_close = commodity_data[f"Close_{self.commodity}"]

        # Ensure they are Series
        if isinstance(stock_close, pd.DataFrame):
            stock_close = stock_close.squeeze()  # Converts single-column DataFrame to Series
        if isinstance(commodity_close, pd.DataFrame):
            commodity_close = commodity_close.squeeze()  # Converts single-column DataFrame to Series

        # Debug to confirm they are Series
        print("Type of stock_close:", type(stock_close))
        print("Type of commodity_close:", type(commodity_close))
        print("Stock Close Head:", stock_close.head())
        print("Commodity Close Head:", commodity_close.head())

        # Drop missing values
        stock_close = stock_close.dropna()
        commodity_close = commodity_close.dropna()

        # Ensure lengths match
        min_length = min(len(stock_close), len(commodity_close))
        stock_close = stock_close.iloc[:min_length]
        commodity_close = commodity_close.iloc[:min_length]

        # Calculate correlation
        correlation_coef = stock_close.corr(commodity_close)

        return crewai.Task(
            description=dedent(f"""
                Analyze the historical price data of {self.stock} and {self.commodity} to calculate their correlation.
                Based on the correlation results, determine how the commodity influences stock performance.
            """),
            agent=self,
            expected_output=f"The correlation between {self.stock} and {self.commodity} is: {correlation_coef:.4f}"
        )


