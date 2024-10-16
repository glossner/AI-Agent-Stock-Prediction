from crewai import Agent

from src.Agents.Analysis.Tools.browser_tools import BrowserTools
from src.Agents.Analysis.Tools.calculator_tools import CalculatorTools
from src.Agents.Analysis.Tools.search_tools import SearchTools
from src.Agents.Analysis.Tools.sec_tools import SECTools
from src.Agents.Agent_Indicators.indicator_agent_rsi import IndicatorAgentRSI
from src.Agents.Agent_Indicators.indicator_agent_sma import IndicatorAgentSMA
from src.Agents.Analysis.trend_detection_agent import TrendDetectionAgent
from src.Agents.Analysis.trend_prediction_agent import TrendPredictionAgent
from src.Agents.Analysis.signal_generation_agent import SignalGenerationAgent

from langchain_community.tools import YahooFinanceNewsTool
from langchain_openai import ChatOpenAI

gpt_model = ChatOpenAI(
  temperature=0,
  model_name="gpt-4o"
)

class StockAnalysisAgents():
  def financial_analyst(self):
    return Agent(
      llm=gpt_model,
      role='The Best Financial Analyst',
      goal="""Impress all customers with your financial data 
      and market trends analysis""",
      backstory="""The most seasoned financial analyst with 
      lots of expertise in stock market analysis and investment
      strategies that is working for a super important customer.""",
      verbose=True,
      tools=[
        BrowserTools.scrape_and_summarize_website,
        SearchTools.search_internet,
        CalculatorTools.calculate,
        SECTools.search_10q,
        SECTools.search_10k
      ]
    )

  def research_analyst(self):
    return Agent(
      llm=gpt_model,
      role='Staff Research Analyst',
      goal="""Being the best at gather, interpret data and amaze
      your customer with it""",
      backstory="""Known as the BEST research analyst, you're
      skilled in sifting through news, company announcements, 
      and market sentiments. Now you're working on a super 
      important customer""",
      verbose=True,
      tools=[
        BrowserTools.scrape_and_summarize_website,
        SearchTools.search_internet,
        SearchTools.search_news,
        YahooFinanceNewsTool(),
        SECTools.search_10q,
        SECTools.search_10k
      ]
  )

  def investment_advisor(self):
    return Agent(
      llm=gpt_model,
      role='Private Investment Advisor',
      goal="""Impress your customers with full analyses over stocks
      and completer investment recommendations""",
      backstory="""You're the most experienced investment advisor
      and you combine various analytical insights to formulate
      strategic investment advice. You are now working for
      a super important customer you need to impress.""",
      verbose=True,
      tools=[
        BrowserTools.scrape_and_summarize_website,
        SearchTools.search_internet,
        SearchTools.search_news,
        CalculatorTools.calculate,
        YahooFinanceNewsTool()
      ]
    )

  def rsi_analyst(self):
    return IndicatorAgentRSI(model="gpt-4o")

  def sma_analyst(self):
    return IndicatorAgentSMA(model="gpt-4o")

  def trend_detection_analyst(self):
    return TrendDetectionAgent(model="gpt-4o")

  def trend_prediction_analyst(self):
    return TrendPredictionAgent(model="gpt-4o")

  def signal_generation_analyst(self):
    return SignalGenerationAgent(model="gpt-4o")
  def signal_generation_analyst(self):
    return SignalGenerationAgent(risk_tolerance='medium')