from src.Agents.base_agent import BaseAgent
import pandas as pd
import pandas_ta as ta
from pydantic import Field

class IndicatorAgentSMA(BaseAgent):
    period: int = Field(default=14, description="The period for SMA calculation")

    def __init__(self, period: int = 14, **kwargs):
        super().__init__(
            role='SMA Indicator Agent',
            goal='Calculate and analyze SMA for stock data',
            backstory='Expert in technical analysis focusing on moving averages',
            **kwargs
        )
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        sma_column_name = f"SMA{self.period}"
        data[sma_column_name] = ta.sma(data['Close'], length=self.period)
        return data

    def respond(self, user_input):
        data = pd.DataFrame(user_input)
        data_with_sma = self.calculate(data)
        current_price = data['Close'].iloc[-1]
        sma_value = data_with_sma[f"SMA{self.period}"].iloc[-1]
        
        if current_price > sma_value:
            analysis = "Bullish"
        elif current_price < sma_value:
            analysis = "Bearish"
        else:
            analysis = "Neutral"
        
        return f"SMA Analysis: {analysis} (SMA: {sma_value:.2f}, Current Price: {current_price:.2f})"

# This is the class that should be imported in app.py
SMAIndicator = IndicatorAgentSMA