from src.Agents.base_agent import BaseAgent
import pandas as pd
import json


class IndicatorAgentSMA(BaseAgent):
    """
        Note: This is for illustrative purposes only. Do not use it as a live agent.
              It costs way too many tokens for Chat-GPT to return what is easily computed by pandas_ta
    """
    def __init__(self, model="gpt-3.5"):
        super().__init__(model=model)  # Call the parent class's __init__ method

    def construct_message(self, data_list, **kwargs):
        period = kwargs.get('period', 14)
        return (
            f"Given the following list of closing prices: {json.dumps(data_list)}, "
            f"calculate the Simple Moving Average (SMA) with a period of {period}. "
            f"Please return the result as a JSON array of SMA values."
        )

    def calculate(self, data: pd.DataFrame, period=14) -> pd.Series:
        data_list = data['Close'].tolist()
        sma_values_json = self.call_model(data_list, period=period)

        # Parse the JSON string into a list of floats
        if sma_values_json:
            try:
                sma_values = json.loads(sma_values_json)
                return pd.Series(sma_values, index=data.index[-len(sma_values):])
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")
                return pd.Series([None] * len(data))
        else:
            return pd.Series([None] * len(data))

    def respond(self, user_input):
        data = pd.DataFrame(user_input)
        sma = self.calculate(data)
        return sma.tolist()
