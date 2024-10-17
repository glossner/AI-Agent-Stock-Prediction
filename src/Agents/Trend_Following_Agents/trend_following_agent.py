
import re
from pydantic import BaseModel, Field
from textwrap import dedent
import crewai as crewai
from src.Agents.base_agent import BaseAgent
#from src.Agents.Analysis.Tools.search_tools import SearchTools


class TrendFollowingAgent(BaseAgent):
    def __init__(self, symbol="AAPL", **kwargs):
        super().__init__(
            role='Trend Following Agent',
            goal='Determine the trend for stocks',
            backstory='Find and interpret market trend directions',
            #tools=[SearchTools.search_news],
            **kwargs)
        self.symbol = symbol

    def find_trend(self):
        return crewai.Task(
            description=dedent(f"""
                Find the current trend for {self.symbol}
                                                         
                "If you do your BEST WORK, I'll give you a $10,000 commission!"
          
                Make sure to use the most recent data as possible.
          
            """),
            agent=self,
            expected_output=f"""An estimate of if {self.symbol} is in an uptrend, downtrend, or side-ways market """
        )

