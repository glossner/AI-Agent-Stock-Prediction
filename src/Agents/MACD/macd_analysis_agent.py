from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Agents.Analysis.Tools.browser_tools import BrowserTools
from src.Agents.Analysis.Tools.calculator_tools import CalculatorTools
from src.Agents.Analysis.Tools.search_tools import SearchTools
from src.Agents.Analysis.Tools.sec_tools import SECTools
from langchain_community.tools import YahooFinanceNewsTool

gpt_model = ChatOpenAI(
  temperature=0,
  model_name="gpt-4o"
)

class MACDAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role='MACD Trading Advisor',
            goal="""Interpret MACD signals and provide actionable insights on market trends. 
            Help traders identify potential bullish or bearish movements and offer advice 
            on whether to buy, sell, or hold a stock.""",
            backstory="""As an expert in technical analysis, this agent specializes in MACD interpretation. 
            It uses its deep knowledge of stock market trends to assist traders in making informed decisions 
            based on the MACD signals."""
        )
    def macd_trading_advisor(self):
        return Agent(
            llm=gpt_model,
            role='MACD Trading Advisor',
            goal="""Interpret MACD signals and provide actionable insights on market trends. 
            Help traders identify potential bullish or bearish movements and offer advice 
            on whether to buy, sell, or hold a stock.""",
            backstory="""As an expert in technical analysis, this agent specializes in MACD interpretation. 
            It uses its deep knowledge of stock market trends to assist traders in making informed decisions 
            based on the MACD signals.""",
            verbose=True,
            tools=[
                BrowserTools.scrape_and_summarize_website,
                SearchTools.search_internet,
                CalculatorTools.calculate,
                SECTools.search_10q,
                SECTools.search_10k,
                YahooFinanceNewsTool()
            ]
        )

    def macd_analysis(self, agent, macd_data):
        """
        A new task to handle the MACD analysis by the financial analyst agent.

        Args:
            agent (object): The agent responsible for analyzing MACD data.
            macd_data (pd.DataFrame): The calculated MACD and Signal Line data.

        Returns:
            Task: A CrewAI task for the agent to analyze the MACD report.
        """
        # Generate a descriptive report of the MACD analysis
        report = "MACD Analysis Report:\n"
        report += macd_data.to_string(index=False)

        # Create the task for the agent to analyze the MACD report
        return Task(
            description=dedent(f"""
                Analyze the following MACD data for the selected stock.
                Focus on identifying bullish or bearish crossovers and
                use this information to suggest potential buy/sell signals.
                The MACD data is as follows:
                {report}

                Your final answer MUST include an interpretation of the MACD and Signal Line
                crossovers, highlighting potential trade opportunities.
                Use the most recent stock data available.
            """),
            agent=agent,
            expected_output="A comprehensive analysis of the MACD and Signal Line, including trade signals and interpretation."
        )

