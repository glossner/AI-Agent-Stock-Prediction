from crewai import Crew
from textwrap import dedent

from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks
from src.Data_Retrieval.data_fetcher import DataFetcher

class FinancialCrew:
  def __init__(self, company):
    self.company = company
    self.data_fetcher = DataFetcher()

  def run(self):
    agents = StockAnalysisAgents()
    tasks = StockAnalysisTasks()

    research_analyst_agent = agents.research_analyst()
    financial_analyst_agent = agents.financial_analyst()
    trend_detection_agent = agents.trend_detection_analyst()
    trend_prediction_agent = agents.trend_prediction_analyst()
    signal_generation_agent = agents.signal_generation_analyst()
    investment_advisor_agent = agents.investment_advisor()

    # Fetch historical data
    stock_data = self.data_fetcher.get_stock_data(self.company)

    research_task = tasks.research(research_analyst_agent, self.company)
    financial_task = tasks.financial_analysis(financial_analyst_agent)
    trend_detection_task = tasks.trend_detection(trend_detection_agent)
    trend_prediction_task = tasks.trend_prediction(trend_prediction_agent)
    signal_generation_task = tasks.signal_generation(signal_generation_agent)
    recommend_task = tasks.recommend(investment_advisor_agent)

    crew = Crew(
      agents=[
        research_analyst_agent,
        financial_analyst_agent,
        trend_detection_agent,
        trend_prediction_agent,
        signal_generation_agent,
        investment_advisor_agent
      ],
      tasks=[
        research_task,
        financial_task,
        trend_detection_task,
        trend_prediction_task,
        signal_generation_task,
        recommend_task
      ],
      verbose=True
    )

    result = crew.kickoff()
    return result

if __name__ == "__main__":
  print("## Welcome to the Advanced Financial Analysis Crew")
  print('-------------------------------')
  company = input(
    dedent("""
      What is the company (or stock ticker) you want to analyze?
    """))
  
  financial_crew = FinancialCrew(company)
  result = financial_crew.run()
  print("\n\n########################")
  print("## Here is the Comprehensive Stock Analysis Report")
  print("########################\n")
  print(result)