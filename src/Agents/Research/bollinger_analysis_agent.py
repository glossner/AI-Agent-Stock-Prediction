from crewai import Agent, Task
from textwrap import dedent

from src.Agents.base_agent import BaseAgent



class BollingerAnalysisAgent(BaseAgent):
   def __init__(self, **kwargs):
        super().__init__(
            role='Bollinger Bands Investment Advisor',
            goal="""Provide actionable buying or selling suggestions by analyzing Bollinger Bands data 
            and determining whether the stock is overbought, oversold, or trending.""",
            backstory="""As a highly skilled investment advisor, you're specialized in analyzing Bollinger Bands to
            provide clear, actionable investment strategies for your clients.""",
            verbose=True,
            **kwargs)
        

   def analyse_bollinger_data(self, bollinger_band_data):
        """
        Create a new task to analyze Bollinger Bands.

        Args:
            agent: The financial analyst agent responsible for analyzing the Bollinger Bands.
            bollinger_bands (dict): The calculated Bollinger Bands.

        Returns:
            Task: The task object for analyzing Bollinger Bands.
        """
        description = dedent(f"""
            Analyze the provided Bollinger Bands data, which includes the Upper Band, Lower Band, 
            and the Moving Average for the stock. Based on these indicators, assess whether the stock 
            is overbought, oversold, or trending sideways. Additionally, provide insights into any 
            trading opportunities that the bands might suggest.

            Your final answer MUST be a comprehensive report discussing whether the stock is overbought 
            or oversold based on the Bollinger Bands, along with any potential trading opportunities.

            Bollinger Bands Data:
            - Upper Band: {bollinger_band_data['Upper Band'].iloc[-1]}
            - Lower Band: {bollinger_band_data['Lower Band'].iloc[-1]}
            - Moving Average: {bollinger_band_data['Moving Average'].iloc[-1]}
        """)

        # Creating and returning the Task object
        return Task(
            description=description,
            agent=self,
            expected_output="A report analyzing the Bollinger Bands data with insights into potential trading opportunities."
        )