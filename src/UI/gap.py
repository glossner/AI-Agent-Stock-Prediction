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

from src.Agents.Bollinger_agent.bollinger_agent import BollingerAnalysisAgents
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.research_analyst_critic_agent import ResearchAnalysisCriticAgent
from src.Agents.Analysis.research_analyst_agent import ResearchAnalystAgent
from src.Indicators.bollinger import BollingerBands  # Import BollingerBands class
from src.Data_Retrieval.data_fetcher import DataFetcher  # Import DataFetcher class


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
    def __init__(self, company):
        self.company = company
        #self.stock_data = stock_data

    def run(self):
        # Initialize agents
        stock_analysis_agents = StockAnalysisAgents()
        bollinger_agents = BollingerAnalysisAgents()
        
        # Initialize agents
        research_analyst_agent = ResearchAnalystAgent(llm=gpt_4o_high_tokens)
        research_analyst_critic_agent = ResearchAnalysisCriticAgent(llm=gpt_4o_high_tokens)
        #financial_analyst_agent = stock_analysis_agents.financial_analyst()
        #investment_advisor_agent = stock_analysis_agents.investment_advisor()
        #bollinger_agent = bollinger_agents.bollinger_bands_investment_advisor()
              
 
        # Bollinger Bands Calculation
        bollinger = BollingerBands(self.stock_data)
        bollinger_bands = bollinger.calculate_bands()

        # Create tasks for Bollinger Bands analysis


        #bollinger_task1_research_analyst = bollinger_agents.bollinger_analysis(research_analyst_agent, bollinger_bands)
        #bollinger_task2_financial_analyst = bollinger_agents.bollinger_analysis(financial_analyst_agent, bollinger_bands)
        #bollinger_task3_investment_advisor = bollinger_agents.bollinger_analysis(investment_advisor_agent, bollinger_bands)
        #bollinger_task4_bollinger = bollinger_agents.bollinger_analysis(bollinger_agent, bollinger_bands)
        
        get_news = research_analyst_agent.get_scenarios_from_news()        
        critique_research_analyst = research_analyst_agent.critique_research_analyst_agent()
        revise_report = research_analyst_agent.revise_report()

        tasks_baseline=[
            get_news,
            critique_research_analyst,
            revise_report
             ]


        tasks_feedback=[
           get_news,
            critique_research_analyst,
            revise_report,
            critique_research_analyst,
            revise_report

            ]
       

        # Kickoff CrewAI agents and tasks
        crew = crewai.Crew(
            agents=[
                research_analyst_agent,
                research_analyst_critic_agent,
            ],
            tasks=tasks_baseline,
            verbose=True,
            process=crewai.Process.sequential
        )

        result = crew.kickoff()
        return result

if __name__ == "__main__":
    print("## Research Interation Analysis")
    print('-------------------------------')

    company='aapl'    
  
    financial_crew = FinancialCrew(company=company)
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