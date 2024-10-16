from src.Agents.base_agent import BaseAgent
import pandas as pd
import pandas_ta as ta
from pydantic import Field

class RSIIndicator(BaseAgent):
    period: int = Field(default=14, description="The period for RSI calculation")

    def __init__(self, **data):
        super().__init__(
            role='RSI Indicator Agent',
            goal='Calculate and analyze RSI for stock data',
            backstory='Expert in technical analysis focusing on momentum indicators',
            **data
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        if 'Close' not in data.columns:
            raise ValueError("DataFrame must contain a 'Close' column")
        
        rsi_column_name = f"RSI_{self.period}"
        data[rsi_column_name] = ta.rsi(data['Close'], length=self.period)
        return data

    def analyze(self, data: pd.DataFrame) -> dict:
        data = self.calculate(data)
        current_price = data['Close'].iloc[-1]
        rsi_value = data[f"RSI_{self.period}"].iloc[-1]
        
        if rsi_value > 70:
            condition = "Overbought"
        elif rsi_value < 30:
            condition = "Oversold"
        else:
            condition = "Neutral"
        
        return {
            "condition": condition,
            "current_price": current_price,
            "rsi_value": rsi_value
        }

    def respond(self, data: pd.DataFrame) -> str:
        analysis = self.analyze(data)
        return f"RSI Analysis: {analysis['condition']} (RSI: {analysis['rsi_value']:.2f}, Current Price: {analysis['current_price']:.2f})"