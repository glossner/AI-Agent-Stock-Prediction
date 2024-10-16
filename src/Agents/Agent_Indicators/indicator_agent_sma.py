from src.Agents.base_agent import BaseAgent
import pandas as pd
import pandas_ta as ta
from pydantic import Field


class SMAIndicator(BaseAgent):
    period: int = Field(default=50, description="The period for SMA calculation")

    def __init__(self, **data):
        super().__init__(
            role='SMA Indicator Agent',
            goal='Calculate and analyze SMA for stock data',
            backstory='Expert in technical analysis focusing on moving averages',
            **data
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        if 'Close' not in data.columns:
            raise ValueError("DataFrame must contain a 'Close' column")
        
        sma_column_name = f"SMA_{self.period}"
        data[sma_column_name] = ta.sma(data['Close'], length=self.period)
        return data

    def analyze(self, data: pd.DataFrame) -> dict:
        data = self.calculate(data)
        current_price = data['Close'].iloc[-1]
        sma_value = data[f"SMA_{self.period}"].iloc[-1]
        
        if current_price > sma_value:
            trend = "Bullish"
        elif current_price < sma_value:
            trend = "Bearish"
        else:
            trend = "Neutral"
        
        return {
            "trend": trend,
            "current_price": current_price,
            "sma_value": sma_value
        }

    def respond(self, data: pd.DataFrame) -> str:
        analysis = self.analyze(data)
        return f"SMA Analysis: {analysis['trend']} (SMA: {analysis['sma_value']:.2f}, Current Price: {analysis['current_price']:.2f})"