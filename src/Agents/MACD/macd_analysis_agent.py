from crewai import Agent
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
        description = dedent(f"""
            Analyze the provided MACD data, which includes the MACD Line, Signal Line, 
            and MACD Histogram. Based on these indicators, assess whether the stock 
            is showing bullish, bearish, or neutral signals. Additionally, provide 
            trading recommendations based on the MACD crossover or divergence.

            Your final answer MUST be a comprehensive report discussing whether the 
            stock is in a bullish or bearish phase and provide buy, sell, or hold recommendations.

            MACD Data:
            - MACD Line: {macd_data['MACD Line'].iloc[-1]}
            - Signal Line: {macd_data['Signal Line'].iloc[-1]}
            - MACD Histogram: {macd_data['MACD Histogram'].iloc[-1]}
        """)

        return Task(
            description=description,
            agent=agent,
            expected_output="A report analyzing MACD signals with trading recommendations."
        )
