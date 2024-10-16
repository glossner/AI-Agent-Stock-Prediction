from src.Agents.base_agent import BaseAgent
from src.Agents.Agent_Indicators.indicator_agent_rsi import IndicatorAgentRSI
from src.Agents.Agent_Indicators.indicator_agent_sma import IndicatorAgentSMA
import pandas as pd

class TrendAnalysisAgent(BaseAgent):
    def __init__(self, model="gpt-4"):
        super().__init__(
            role='Trend Analysis Agent',
            goal='Analyze market trends using multiple indicators',
            backstory='Expert in combining various technical indicators for comprehensive trend analysis',
            model=model
        )
        self.rsi_agent = IndicatorAgentRSI()
        self.sma_agent = IndicatorAgentSMA()

    def analyze_trend(self, data: pd.DataFrame) -> str:
        rsi_analysis = self.rsi_agent.respond(data)
        sma_analysis = self.sma_agent.respond(data)

        rsi_signal = rsi_analysis.split(":")[1].strip()
        sma_signal = sma_analysis.split(":")[1].strip()

        if "Bullish" in sma_signal and "Overbought" not in rsi_signal:
            return "Strong Uptrend"
        elif "Bearish" in sma_signal and "Oversold" not in rsi_signal:
            return "Strong Downtrend"
        elif "Neutral" in sma_signal:
            return "Sideways"
        else:
            return "Mixed Signals"

    def respond(self, user_input):
        data = pd.DataFrame(user_input)
        trend = self.analyze_trend(data)
        return f"Trend Analysis: {trend}"