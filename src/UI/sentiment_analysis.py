import os
from crewai import Crew
from dotenv import load_dotenv
from textwrap import dedent

# Load environment variables (API keys)
load_dotenv()

class SentimentCrew:
    def __init__(self, stock_or_sector):
        self.stock_or_sector = stock_or_sector

    def run(self):
        agents = self.init_agents()
        tasks = self.init_tasks(agents)

        crew = Crew(
            agents=[agents['research_analyst'], agents['sentiment_analyst']],
            tasks=[tasks['news_sentiment'], tasks['actionable_advice']],
            verbose=True
        )

        result = crew.kickoff()
        return result

    def init_agents(self):
        from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
        agents = StockAnalysisAgents()
        return {
            'research_analyst': agents.research_analyst(),
            'sentiment_analyst': agents.sentiment_analyst()
        }

    def init_tasks(self, agents):
        from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks
        tasks = StockAnalysisTasks()

        news_data = tasks.fetch_news(self.stock_or_sector)

        return {
            'news_sentiment': tasks.analyze_sentiment(agents['sentiment_analyst'], news_data),
            'actionable_advice': tasks.provide_investment_advice(agents['sentiment_analyst'], news_data)
        }

if __name__ == "__main__":
    print("## Sentiment Analysis for Financial News Articles")
    print('-------------------------------')
    stock_or_sector = input(
        dedent("""\n
        Enter the stock or sector you want to analyze:
        """)
    )

    sentiment_crew = SentimentCrew(stock_or_sector)
    result = sentiment_crew.run()

    print("\n\n########################")
    print("## Sentiment Analysis Report")
    print("########################\n")
    print(result)
