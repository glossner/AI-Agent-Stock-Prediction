from src.Agents.Agent_Indicators.indicator_agent import IndicatorAgent
import pandas as pd
import json

class IndicatorAgentRSI(IndicatorAgent):
    def __init__(self, model="gpt-4o"):
        super().__init__(model=model)  # Call the parent class's __init__ method

    def construct_message(self, data_list, **kwargs):
        period = kwargs.get('period', 14)  # Default to 14 if not provided
        return f"Calculate the RSI for this data: {json.dumps(data_list)}, with a period of {period}."

    def calculate(self, data: pd.DataFrame, period=14) -> pd.Series:
        data_list = data['Close'].tolist()
        rsi_values = self.call_model(data_list, period=period)
        return pd.Series(rsi_values, index=data.index)

    def respond(self, user_input):
        data = pd.DataFrame(user_input)
        rsi = self.calculate(data)
        return rsi.tolist()
