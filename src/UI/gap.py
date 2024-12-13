# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import os
import sys
import crewai as crewai
#from crewai import Crew
from textwrap import dedent
import logging
import crewai as crewai
import langchain_openai as lang_oai
import crewai_tools as crewai_tools

from src.Helpers.pretty_print_crewai_output import display_crew_output

from src.Indicators.bollinger import BollingerBands  # Import BollingerBands class
from src.Data_Retrieval.data_fetcher import DataFetcher  # Import DataFetcher class
from src.Agents.Research.research_analyst_critic_agent import ResearchAnalysisCriticAgent
from src.Agents.Research.research_analyst_agent import ResearchAnalystAgent
from src.Agents.Research.bollinger_analysis_agent import BollingerAnalysisAgent
from src.Agents.Research.bollinger_buy_sell_agent import BollingerBuySellAgent


# Initialize logger
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

gpt_4o_high_tokens = lang_oai.ChatOpenAI(
    model_name="gpt-4o",
    temperature=0.0,
    max_tokens=1500
)


class FinancialCrew:
    def __init__(self, ticker):
        self.ticker = ticker
        self.stock_data = DataFetcher().get_stock_data(ticker)

    def run(self):
        # Initialize agents
        #stock_analysis_agents = StockAnalysisAgents()
        
        # Bollinger Bands Data Calculation
        bollinger_data = BollingerBands(self.stock_data)
        bollinger_bands_data = bollinger_data.calculate_bands()


        # Initialize agents
        research_analyst_agent = ResearchAnalystAgent(ticker=self.ticker, llm=gpt_4o_high_tokens)
        research_analyst_critic_agent = ResearchAnalysisCriticAgent(llm=gpt_4o_high_tokens)
        bollinger_investment_advisor_agent = BollingerAnalysisAgent(llm=gpt_4o_high_tokens)
        bollinger_buy_sell_agent = BollingerBuySellAgent(ticker=self.ticker, llm=gpt_4o_high_tokens)

        agents = [research_analyst_agent, research_analyst_critic_agent, bollinger_investment_advisor_agent, bollinger_buy_sell_agent]
              
 


        # Create tasks for Bollinger Bands analysis        
        get_news = research_analyst_agent.get_scenarios_from_news()        
        critique_research_analyst = research_analyst_critic_agent.critique_research_analyst_agent()
        revise_report = research_analyst_agent.revise_report()
        analyze_bollinger_data = bollinger_investment_advisor_agent.analyse_bollinger_data(bollinger_bands_data)
        buy_sell_decision = bollinger_buy_sell_agent.buy_sell_decision()

        tasks_baseline=[
            get_news,
            critique_research_analyst,
            revise_report,
            analyze_bollinger_data,
            buy_sell_decision
             ]


        tasks_feedback=[
           get_news,
            critique_research_analyst,
            revise_report,
            critique_research_analyst,
            revise_report,
            analyze_bollinger_data,
            buy_sell_decision
            ]
       

        # Kickoff CrewAI agents and tasks
        crew = crewai.Crew(
            agents=agents,
            tasks=tasks_baseline,
            verbose=True,
            process=crewai.Process.sequential
        )

        result = crew.kickoff()
        return result

if __name__ == "__main__":
    print("## Research Interation Analysis")
    print('-------------------------------')

    ticker='aapl'    
  
    financial_crew = FinancialCrew(ticker=ticker)
    logging.info("Financial crew initialized successfully")

    try:
        crew_output = financial_crew.run()
        logging.info("Financial crew execution run() successfully")
    except Exception as e:
        logging.error(f"Error during crew execution: {e}")
        sys.exit(1)
    
    # Accessing the crew output
    print("\n\n########################")
    print("## Here is the Report")
    print("########################\n")

    display_crew_output(crew_output)

    print("Collaboration complete")
    sys.exit(0)