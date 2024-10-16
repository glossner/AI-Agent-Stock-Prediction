from src.Agents.base_agent import BaseAgent
import pandas as pd
import pandas_ta as ta

class IndicatorAgentRSI(BaseAgent):
    def __init__(self, model="gpt-3.5"):
        super().__init__(
            role='RSI Indicator Agent',
            goal='Calculate and analyze RSI for stock data',
            backstory='Expert in technical analysis focusing on RSI calculations',
            model=model
        )

    def calculate(self, data: pd.DataFrame, period=14) -> pd.Series:
        return ta.rsi(data['Close'], length=period)

    def analyze(self, rsi_values: pd.Series) -> str:
        latest_rsi = rsi_values.iloc[-1]
        if latest_rsi > 70:
            return "Overbought"
        elif latest_rsi < 30:
            return "Oversold"
        else:
            return "Neutral"

    def respond(self, user_input):
        data = pd.DataFrame(user_input)
        rsi = self.calculate(data)
        analysis = self.analyze(rsi)
        return f"RSI Analysis: {analysis} (RSI: {rsi.iloc[-1]:.2f})"