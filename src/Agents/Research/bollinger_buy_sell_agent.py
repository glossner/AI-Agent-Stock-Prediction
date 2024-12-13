import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
import logging

class BollingerBuySellAgent(BaseAgent):
    def __init__(self, ticker="AAPL", **kwargs):
        super().__init__(
            role='Make buy sell decisions for a ticker',
            goal="Evaluate all the data provided and make a decision on whether to buy or sell the ticker",
            backstory="You are a seasoned trader who buys and sells tickers.",
            verbose=True,
            tools=[], 
            allow_delegation=False,
            **kwargs
        )
        self.ticker = ticker
        logging.info("BollingerBuySellAgent initialized")

    def buy_sell_decision(self):
        logging.info("Bollinger buys/sell CrewAI Task being assembled")
        return crewai.Task(
            description=dedent(f"""
                Based on the information given to you that may include news and bollinger band data,
                decide whether {self.ticker} is a buy or sell.
                You get to keep a 10% commission on profits.                                          
            """),
            agent=self,
            expected_output="A buy or sell decisioin signal that can be used to trade the ticker"
        )