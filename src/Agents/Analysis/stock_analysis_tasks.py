######################################
# This code comes from: https://github.com/crewAIInc/crewAI-examples/blob/main/stock_analysis/stock_analysis_agents.py
# And is licensed under MIT
######################################

from crewai import Agent

from src.Agents.Analysis.Tools.browser_tools import BrowserTools
from src.Agents.Analysis.Tools.calculator_tools import CalculatorTools
from src.Agents.Analysis.Tools.search_tools import SearchTools
from src.Agents.Analysis.Tools.sec_tools import SECTools

from langchain_community.tools import YahooFinanceNewsTool
from langchain_openai import ChatOpenAI


gpt_model = ChatOpenAI(
  temperature=0,
  #model_name="gpt-3.5-turbo",
  model_name="gpt-4o"
)

class StockAnalysisAgents():
  def __init__(
          self,
          gpt_model=gpt_model
     ):
      self.gpt_model = gpt_model

  def financial_analyst(self):
    return Agent(
      llm=self.gpt_model,
      role='The Best Financial Analyst',
      goal="""Impress all customers with your financial data 
      and market trends analysis""",
      backstory="""The most seasoned financial analyst with 
      lots of expertise in stock market analysis and investment
      strategies that is working for a super important customer.""",
      verbose=True,
      tools=[
        #BrowserTools.scrape_and_summarize_website,
        SearchTools.search_internet,
        CalculatorTools.calculate,
        SECTools.search_10q,
        SECTools.search_10k
      ]
    )

  def research_analyst(self):
    return Agent(
      llm=self.gpt_model,
      role='Staff Research Analyst',
      goal="""Being the best at gather, interpret data and amaze
      your customer with it""",
      backstory="""Known as the BEST research analyst, you're
      skilled in sifting through news, company announcements, 
      and market sentiments. Now you're working on a super 
      important customer""",
      verbose=True,
      tools=[
        #BrowserTools.scrape_and_summarize_website,
        SearchTools.search_internet,
        SearchTools.search_news,
        YahooFinanceNewsTool(),
        SECTools.search_10q,
        SECTools.search_10k
      ]
  )

  def investment_advisor(self):
    return Agent(
      llm=self.gpt_model,
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

  
  def sentiment_analyst(self):
        return Agent(
            llm=self.gpt_model,
            role='Sentiment Analyst',
            goal="""Analyze market sentiments from news articles and derive actionable insights for investments.""",
            backstory="""You're an expert in sentiment analysis, providing insights that help in determining market impact and investment decisions.""",
            verbose=True,
            tools=[
                SearchTools.search_internet,
                CalculatorTools.calculate
            ]
        )


  def dividend_forecasting_agent(self, company):
        '''
        Forcast dividends for any company ticker
        '''
        return Agent(
            llm=self.gpt_model,
            role=f'Dividend Forecasting Agent for {company}',
            goal=f"""Provide a detailed dividend growth forecast based on {company}'s
            income statement and cash flow statement.""",
            backstory=f"""You are a seasoned financial analyst specializing in dividend
            forecasting. You are tasked with analyzing {company}'s key financial documents 
            such as income statements, cash flow statements, and historical dividend payouts 
            to provide a well-researched dividend growth forecast.""",
            verbose=True
        )

    
  def economic_forecasting_agent(self):
        return Agent(
            llm=self.gpt_model,
            role='Economic Analyst',
            goal="""Analyze macroeconomic indicators, government policy changes, and financial reports
            to predict which sectors are likely to perform well in the coming quarters.""",
            backstory="""You are an experienced economic analyst, adept at understanding the effects of macroeconomic factors
            and policy changes on various sectors of the economy. You have access to the latest macroeconomic data and financial reports.""",
            verbose=True,
            tools=[]
        )


