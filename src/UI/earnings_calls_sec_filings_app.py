# financial_analysis.py

import os
from yahooquery import Ticker
import requests
from crewai import Crew
from textwrap import dedent
from dotenv import load_dotenv
import time
import json
import warnings
from cryptography.utils import CryptographyDeprecationWarning
import tiktoken
import openai  # Added import

from langchain_openai import ChatOpenAI  # Added import

# Suppress CryptographyDeprecationWarning (Optional)
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

# Initialize the GPT model
gpt_model = ChatOpenAI(
    temperature=0,
    model_name="gpt-4o"
)

# Load environment variables from .env file
load_dotenv()

class FinancialCrew:
    def __init__(self, company, exchange):
        self.company = company
        self.exchange = exchange
        self.earnings_api_key = os.getenv("EARNINGSCAST_API_KEY", "demo")
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def count_tokens(self, text, model="gpt-4"):
        """
        Count the number of tokens in the given text for the specified model.
        """
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))

    def summarize_transcript(self, transcript, max_tokens=1500):  # Reduced from 2000 to 1500
        """
        Summarize the transcript to reduce token usage.
        If the transcript is too long, truncate it before summarization.
        """
        token_count = self.count_tokens(transcript)
        if token_count > max_tokens:
            # Truncate the transcript to fit within max_tokens
            encoding = tiktoken.encoding_for_model("gpt-4")
            tokens = encoding.encode(transcript)[:max_tokens]
            truncated_transcript = encoding.decode(tokens)
            transcript = truncated_transcript
            print(f"Transcript truncated to {max_tokens} tokens.")

        prompt = f"Please provide a concise summary of the following earnings call transcript:\n\n{transcript}"
        try:
            summary = gpt_model(prompt)
            return summary
        except openai.RateLimitError as e:
            print(f"Rate limit exceeded during summarization: {e}. Retrying...")
            time.sleep(5)  # Wait before retrying
            return self.summarize_transcript(transcript, max_tokens)
        except Exception as e:
            print(f"Error during summarization: {e}")
            return transcript  # Fallback to original transcript

    def fetch_sec_filings(self):
        """
        Fetch SEC filings for the specified company using YahooQuery.
        To reduce token usage, only relevant sections are extracted and limited to the first 10 filings.
        """
        ticker = Ticker(self.company)
        sec_filings = ticker.sec_filings
        if sec_filings.empty:
            print("No SEC filings found for the company.")
            return None
        
        # Debugging: Print the columns and first few rows
        print("SEC Filings Columns:", sec_filings.columns.tolist())
        print("SEC Filings Sample Data:\n", sec_filings.head())
        
        # Define desired columns
        desired_columns = ['form', 'filing_date', 'filed_at', 'url']
        
        # Find available columns from desired list
        available_columns = [col for col in desired_columns if col in sec_filings.columns]
        if available_columns:
            relevant_sections = sec_filings[available_columns].head(10)
            print(f"Selected columns for SEC filings: {available_columns}")
        else:
            print("None of the desired columns are available. Using all available data.")
            relevant_sections = sec_filings.head(10)
        
        return relevant_sections.to_json()

    def fetch_earnings_calls(self):
        """
        Fetch earnings call events using the EarningsCast API.
        Implements retries with exponential backoff in case of rate limiting.
        """
        url = f'https://v2.api.earningscall.biz/events?apikey={self.earnings_api_key}&exchange={self.exchange}&symbol={self.company}'
        response = self.make_request(url)
        if response:
            return response.json()
        else:
            print("Error fetching earnings calls.")
            return None

    def fetch_earnings_transcript(self, year, quarter):
        """
        Fetch a specific earnings call transcript using the EarningsCast API.
        Implements retries with exponential backoff in case of rate limiting.
        """
        url = f'https://v2.api.earningscall.biz/transcript?apikey={self.earnings_api_key}&exchange={self.exchange}&symbol={self.company}&year={year}&quarter={quarter}'
        response = self.make_request(url)
        if response:
            return response.json().get('text')
        else:
            print(f"Error fetching earnings transcript for {year} Q{quarter}.")
            return None

    def make_request(self, url):
        """
        Makes an HTTP GET request with retry logic for handling rate limits and transient errors.
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Error fetching data: {response.status_code}")
                    return None
            except requests.exceptions.RequestException as e:
                delay = self.retry_delay * (2 ** attempt)
                print(f"Request exception: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
        print("Max retries exceeded.")
        return None

    def run(self):
        """
        Initializes agents and tasks, then executes the analysis using Crew.
        """
        agents = self.init_agents()
        tasks = self.init_tasks(agents)

        crew = Crew(
            agents=list(agents.values()),
            tasks=list(tasks.values()),
            verbose=True
        )

        result = crew.kickoff()
        return result

    def init_agents(self):
        """
        Initializes the required agents from the earnings_sec_analysis_agents module.
        """
        from src.Agents.Earnings_Calls_Sec_Filings_Agents.earnings_sec_analysis_agents import EarningsSecAnalysisAgents
        agents_module = EarningsSecAnalysisAgents()
        return {
            'financial_analyst': agents_module.financial_analyst(),
            'sentiment_analyst': agents_module.sentiment_analyst()
        }

    def init_tasks(self, agents):
        """
        Initializes tasks by fetching data and creating tasks for each agent.
        """
        from src.Agents.Earnings_Calls_Sec_Filings_Agents.earnings_sec_analysis_agents import EarningsSecAnalysisAgents
        tasks_module = EarningsSecAnalysisAgents()

        # Fetch SEC filings and earnings call data
        sec_data = self.fetch_sec_filings()
        earnings_data = self.fetch_earnings_calls()

        # Fetch transcripts for each earnings call event
        transcripts = {}
        if earnings_data and 'events' in earnings_data:
            for event in earnings_data['events']:
                year = event.get('year')
                quarter = event.get('quarter')
                if year and quarter:
                    transcript = self.fetch_earnings_transcript(year, quarter)
                    if transcript:
                        key = f"{year} Q{quarter}"
                        summarized_transcript = self.summarize_transcript(transcript)
                        transcripts[key] = summarized_transcript
                        # To prevent large token usage, limit the number of transcripts
                        if len(transcripts) >= 1:  # Reduce to 1 transcript
                            break

        # Create individual tasks for each transcript to manage token usage
        transcript_tasks = {}
        for key, text in transcripts.items():
            task_key = f"transcript_sentiment_analysis_{key.replace(' ', '_')}"
            transcript_tasks[task_key] = tasks_module.analyze_single_earnings_transcript(
                agents['sentiment_analyst'], key, text
            )

        return {
            'financial_analysis': tasks_module.analyze_sec_filings(agents['financial_analyst'], sec_data),
            'earnings_sentiment_analysis': tasks_module.analyze_earnings_calls(agents['sentiment_analyst'], earnings_data),
            **transcript_tasks
        }

if __name__ == "__main__":
    print("## Welcome to Financial Analysis Crew")
    print('-------------------------------')
    company = input("What is the company you want to analyze? ").strip().upper()
    exchange = input("What is the exchange (e.g., NASDAQ, NYSE)? ").strip().upper()

    financial_crew = FinancialCrew(company, exchange)
    result = financial_crew.run()

    print("\n\n########################")
    print("## Analysis Report")
    print("########################\n")
    print(result)

'''
    # Extract and serialize the analysis data
    try:
        # Assuming these are the relevant attributes
        financial_analysis = result.financial_analysis
        earnings_sentiment_analysis = result.earnings_sentiment_analysis
        transcript_sentiment_analysis = getattr(result, 'transcript_sentiment_analysis_2024_Q4', None)

        analysis_report = {
            "financial_analysis": financial_analysis,
            "earnings_sentiment_analysis": earnings_sentiment_analysis,
            "transcript_sentiment_analysis_2024_Q4": transcript_sentiment_analysis
        }

        # Serialize the analysis report
        analysis_json = json.dumps(analysis_report, indent=4)

        # Print the JSON-formatted analysis report
        print(analysis_json)
    except Exception as e:
        print(f"Error serializing the analysis report: {e}")
'''