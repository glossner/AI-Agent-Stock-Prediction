# src/Agents/Earnings_Calls_Sec_Filings_Agents/earnings_sec_analysis_agents.py

from crewai import Agent, Task
from textwrap import dedent
from langchain_openai import ChatOpenAI

# Initialize the GPT-4 model
gpt_model = ChatOpenAI(
    temperature=0,
    model_name="gpt-4"
)

class EarningsSecAnalysisAgents:
    def financial_analyst(self):
        """
        Initializes the Financial Analyst agent.
        """
        return Agent(
            llm=gpt_model,
            role='Financial Analyst',
            goal="Provide comprehensive analysis of SEC filings to guide investment decisions.",
            backstory="You are an expert financial analyst with deep knowledge of financial statements, market trends, and SEC regulations.",
            verbose=True
        )
    
    def sentiment_analyst(self):
        """
        Initializes the Sentiment Analyst agent.
        """
        return Agent(
            llm=gpt_model,
            role='Sentiment Analyst',
            goal="Assess the sentiment and tone of management during earnings calls.",
            backstory="You analyze the language and sentiment used by company executives to gauge confidence and future outlook.",
            verbose=True
        )
    
    def analyze_sec_filings(self, agent, sec_data):
        """
        Creates a task for analyzing SEC filings.
        """
        return Task(
            description=dedent(f"""
                Analyze the SEC filings for potential risks, growth opportunities, and 
                financial trends. Focus on identifying patterns in the income statement,
                balance sheet, and cash flow.
                SEC Data: {sec_data}
            """),
            agent=agent,
            expected_output="A detailed analysis of SEC filings highlighting investment risks, growth opportunities, and financial trends."
        )
    
    def analyze_earnings_calls(self, agent, earnings_data):
        """
        Creates a task for analyzing earnings calls.
        """
        return Task(
            description=dedent(f"""
                Analyze the earnings calls for insights on the company's performance, market outlook, and 
                future guidance. Identify management's tone and sentiment.
                Earnings Data: {earnings_data}
            """),
            agent=agent,
            expected_output="A detailed earnings call analysis with insights into company performance, market outlook, and management sentiment."
        )
    
    def analyze_single_earnings_transcript(self, agent, key, transcript):
        """
        Creates a task for analyzing a single earnings call transcript.
        """
        return Task(
            description=dedent(f"""
                Analyze the earnings call transcript for {key} for detailed insights into the company's performance, 
                strategic initiatives, and future plans. Pay attention to management's language, sentiment, 
                and any indications of future growth or challenges.
                Transcript: {transcript}
            """),
            agent=agent,
            expected_output=f"A comprehensive analysis of the {key} earnings call transcript, highlighting key insights, sentiment, and strategic directions."
        )
