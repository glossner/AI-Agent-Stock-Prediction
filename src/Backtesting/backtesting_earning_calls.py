import os
import pandas as pd
import requests
import backtrader as bt
from yahooquery import Ticker
from dotenv import load_dotenv
from crewai import Crew, Agent, Task
from langchain_openai import ChatOpenAI
from textwrap import dedent

# Load API keys
load_dotenv()
EARNINGSCAST_API_KEY = os.getenv("EARNINGSCAST_API_KEY", "demo")

# Initialize the GPT model
gpt_model = ChatOpenAI(
    temperature=0,
    model_name="gpt-4"
)

# Define EarningsSecAnalysisAgents
class EarningsSecAnalysisAgents:
    def financial_analyst(self):
        return Agent(
            llm=gpt_model,
            role='Financial Analyst',
            goal="Provide concise analysis based on SEC filings and earnings calls to guide a single investment decision.",
            backstory="You are an expert financial analyst with deep knowledge of market trends and SEC regulations.",
            verbose=True
        )

    def analyze_sec_filings(self, agent, sec_data):
        key_sections = ["Risk Factors", "Financial Data", "Management's Discussion and Analysis"]
        tasks = []
        
        for section in key_sections:
            if section in sec_data:
                sec_text = sec_data[section][:1000]  # Limit each section to 1000 chars if necessary
                task = Task(
                    description=dedent(f"""
                        Provide a brief analysis of potential risks and opportunities from the {section} section of SEC filings.
                        Key financial trends and highlights only.
                        {section} Data: {sec_text}
                    """),
                    agent=agent,
                    expected_output=f"A concise analysis of the {section} section."
                )
                tasks.append(task)
        
        return tasks

    def analyze_earnings_calls(self, agent, earnings_data):
        trimmed_earnings_data = earnings_data[:1000]  # Limit data to the first 1000 characters
        return Task(
            description=dedent(f"""
                Summarize any notable market insights or guidance from the earnings call.
                Key highlights only.
                Earnings Data: {trimmed_earnings_data}
            """),
            agent=agent,
            expected_output="A brief earnings call analysis with key insights into company performance and outlook."
        )

# FinancialCrew class for fetching and analyzing data
class FinancialCrew:
    def __init__(self, company, exchange):
        self.company = company
        self.exchange = exchange
        self.earnings_api_key = EARNINGSCAST_API_KEY

    def fetch_sec_filings(self):
        ticker = Ticker(self.company)
        sec_filings = ticker.sec_filings
        if sec_filings.empty:
            print("No SEC filings found for the company.")
            return None
        return sec_filings.to_dict()

    def fetch_earnings_calls(self):
        url = f'https://v2.api.earningscall.biz/events?apikey={self.earnings_api_key}&exchange={self.exchange}&symbol={self.company}'
        response = requests.get(url)
        if response.status_code == 200:
            earnings_data = response.json()
            return earnings_data[0] if isinstance(earnings_data, list) and earnings_data else None
        else:
            print("Error fetching earnings calls:", response.status_code)
            return None

    def analyze_single_signal(self):
        agents = EarningsSecAnalysisAgents()
        financial_analyst = agents.financial_analyst()

        sec_data = self.fetch_sec_filings()
        earnings_data = self.fetch_earnings_calls()

        signal = None
        signal_date = None

        if sec_data:
            sec_analysis_tasks = agents.analyze_sec_filings(financial_analyst, sec_data)
            sec_analysis_result = ""
            for task in sec_analysis_tasks:
                crew = Crew(agents=[financial_analyst], tasks=[task], verbose=True)
                result = crew.kickoff()
                sec_analysis_result += getattr(result, 'text', '') or getattr(result, 'output', '')

            if sec_analysis_result:
                signal = self.determine_signal(sec_analysis_result)
                signal_date = pd.to_datetime("today").date()
        elif earnings_data:
            earnings_analysis_task = agents.analyze_earnings_calls(financial_analyst, earnings_data)
            crew = Crew(agents=[financial_analyst], tasks=[earnings_analysis_task], verbose=True)
            result = crew.kickoff()
            earnings_analysis_result = getattr(result, 'text', '') or getattr(result, 'output', '')
            if earnings_analysis_result:
                signal = self.determine_signal(earnings_analysis_result)
                signal_date = pd.to_datetime("today").date()

        if signal:
            print(f"Generated single signal: {signal} on {signal_date}")
            return {'date': signal_date, 'signal': signal}
        else:
            print("No valid signal generated.")
            return None

    def determine_signal(self, analysis_result):
        if 'positive' in analysis_result.lower():
            return 'Buy'
        elif 'negative' in analysis_result.lower():
            return 'Sell'
        else:
            return 'Hold'

# Backtrader strategy using crewAI agent single in-memory signal
class CrewAIStrategy(bt.Strategy):
    params = (('signal_data', None),)

    def __init__(self):
        self.signal_data = self.params.signal_data
        self.dataclose = self.datas[0].close

    def next(self):
        if self.signal_data:
            signal_date = self.signal_data['date']
            signal = self.signal_data['signal']
            
            if self.datas[0].datetime.date(0) == signal_date:
                if signal == 'Buy' and not self.position:
                    self.buy()
                    print(f"{signal_date} - Buy at {self.dataclose[0]:.2f}")
                elif signal == 'Sell' and self.position:
                    self.close()
                    print(f"{signal_date} - Sell at {self.dataclose[0]:.2f}")
                self.signal_data = None

# Function to run single trade backtest
def run_single_trade_backtest(company_symbol, exchange):
    financial_crew = FinancialCrew(company_symbol, exchange)
    single_signal = financial_crew.analyze_single_signal()

    if not single_signal:
        print("No signal generated. Exiting backtest.")
        return

    cerebro = bt.Cerebro()

    signal_date = single_signal['date']
    start_date = signal_date - pd.Timedelta(days=5)
    end_date = signal_date + pd.Timedelta(days=5)

    data = bt.feeds.YahooFinanceData(
        dataname=company_symbol,
        fromdate=start_date,
        todate=end_date,
        reverse=False
    )

    cerebro.adddata(data)
    cerebro.addstrategy(CrewAIStrategy, signal_data=single_signal)
    cerebro.broker.setcash(100000.0)

    print("Starting backtest for a single trade...")
    cerebro.run()
    print("Backtest completed.")

    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - 100000.0

    print(f"Final Portfolio Value: ${portvalue:,.2f}")
    print(f"Net P/L for single trade: ${pnl:,.2f}")
    cerebro.plot(style='candlestick')

# Entry point
if __name__ == '__main__':
    company_symbol = 'AAPL'  # Example: Apple Inc.
    exchange = 'NASDAQ'
    run_single_trade_backtest(company_symbol, exchange)
