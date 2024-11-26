import os
import re
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics import mean_absolute_error
from crewai import Crew
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks
from src.Agents.divergence_agents.divergence_agent import DivergenceAnalysisAgents, DivergenceAnalysisTasks
from src.Data_Retrieval.data_fetcher import DataFetcher
from src.Indicators.rsi_divergence import RSIIndicator
from src.Indicators.macd_indicator import MACDIndicator
from src.Indicators.detect_divergence import DivergenceDetector

# Load environment variables
load_dotenv()

class FinancialCrew:
    def __init__(self, company, indicator_name):
        self.company = company
        self.indicator_name = indicator_name

    def run(self):
        # Initialize agents and tasks
        agents = StockAnalysisAgents()
        divergence_agents = DivergenceAnalysisAgents()
        tasks = StockAnalysisTasks()
        divergence_tasks = DivergenceAnalysisTasks()

        # Initialize the divergence trading advisor agent
        divergence_agent = divergence_agents.divergence_trading_advisor()

        # Fetch stock data
        data_fetcher = DataFetcher()
        stock_data = data_fetcher.get_stock_data(self.company)

        # Calculate MACD or RSI data
        if self.indicator_name == 'MACD':
            indicator_data = MACDIndicator().calculate(stock_data)
        elif self.indicator_name == 'RSI':
            indicator_data = RSIIndicator().calculate(stock_data)
        else:
            raise ValueError(f"Unsupported indicator: {self.indicator_name}")

        # Create a divergence detection task
        divergence_task = divergence_tasks.detect_divergence(
            divergence_agent, stock_data, indicator_data, self.indicator_name
        )

        # Kickoff CrewAI agents and tasks
        crew = Crew(
            agents=[divergence_agent],
            tasks=[divergence_task],
            verbose=True
        )

        result = crew.kickoff()
        return result

class Backtester:
    def __init__(self, company, indicator_name):
        self.company = company
        self.indicator_name = indicator_name
        self.data_fetcher = DataFetcher()

    def fetch_stock_data(self):
        return self.data_fetcher.get_stock_data(self.company)

    def calculate_indicator(self, stock_data):
        if self.indicator_name == 'RSI':
            indicator = RSIIndicator()
        elif self.indicator_name == 'MACD':
            indicator = MACDIndicator()
        else:
            raise ValueError(f"Unsupported indicator: {self.indicator_name}")
        return indicator.calculate(stock_data)

    def run_crewai_system(self, stock_data, indicator_data):
        financial_crew = FinancialCrew(self.company, self.indicator_name)
        crew_output = financial_crew.run()

        # Debug: Inspect CrewOutput structure
        print("Inspecting CrewOutput structure...")
        print(crew_output)

        # Extract divergence signals from CrewOutput
        bullish_divergence_dates, bearish_divergence_dates = self.extract_divergence_signals(crew_output)

        return bullish_divergence_dates, bearish_divergence_dates

    def extract_divergence_signals(self, crew_output):
        """
        Extracts bullish and bearish divergence dates from CrewOutput.
        Parses the raw text to find dates mentioned in the narrative.
        """
        bullish_divergence_dates = []
        bearish_divergence_dates = []

        try:
            # Access the raw text from CrewOutput
            if hasattr(crew_output, 'tasks_output') and len(crew_output.tasks_output) > 0:
                task_output = crew_output.tasks_output[0]

                if hasattr(task_output, 'raw'):
                    raw_text = task_output.raw
                    print(f"Raw CrewOutput Text:\n{raw_text}\n")

                    # Use regex to extract dates from the raw text
                    bullish_pattern = r'Bullish Divergences?:\s*([\d-]+\s*\d{2}:\d{2}:\d{2}(?:,\s*[\d-]+\s*\d{2}:\d{2}:\d{2})*)'
                    bearish_pattern = r'Bearish Divergences?:\s*([\d-]+\s*\d{2}:\d{2}:\d{2}(?:,\s*[\d-]+\s*\d{2}:\d{2}:\d{2})*)'

                    bullish_match = re.search(bullish_pattern, raw_text, re.IGNORECASE)
                    bearish_match = re.search(bearish_pattern, raw_text, re.IGNORECASE)

                    if bullish_match:
                        bullish_dates_str = bullish_match.group(1)
                        bullish_divergence_dates = [
                            pd.to_datetime(date.strip()) for date in bullish_dates_str.split(',')
                        ]
                        print(f"Extracted Bullish Divergence Dates: {bullish_divergence_dates}")
                    else:
                        print("No Bullish Divergence dates found in the CrewOutput.")

                    if bearish_match:
                        bearish_dates_str = bearish_match.group(1)
                        bearish_divergence_dates = [
                            pd.to_datetime(date.strip()) for date in bearish_dates_str.split(',')
                        ]
                        print(f"Extracted Bearish Divergence Dates: {bearish_divergence_dates}")
                    else:
                        print("No Bearish Divergence dates found in the CrewOutput.")
                else:
                    print("TaskOutput does not have a 'raw' attribute.")
            else:
                print("No task output found in CrewOutput.")
        except Exception as e:
            print(f"Error extracting divergence signals: {e}")

        return bullish_divergence_dates, bearish_divergence_dates

    def run_non_crewai_system(self, stock_data, indicator_data):
        detector = DivergenceDetector(stock_data, indicator_data, self.indicator_name)
        bullish_signals = detector.detect_bullish_divergence()
        bearish_signals = detector.detect_bearish_divergence()
        return bullish_signals, bearish_signals

    def simulate_trades(self, stock_data, bullish_signals, bearish_signals):
        """
        Simulate trades based on divergence signals.
        Buy on bullish divergence, sell on bearish divergence.
        """
        position = 0  # 0: no position, 1: long
        trades = []
        for date in stock_data.index:
            if date in bullish_signals and position == 0:
                # Buy signal
                price = stock_data.loc[date, 'Close']
                trades.append({'Date': date, 'Type': 'Buy', 'Price': price})
                position = 1
            elif date in bearish_signals and position == 1:
                # Sell signal
                price = stock_data.loc[date, 'Close']
                trades.append({'Date': date, 'Type': 'Sell', 'Price': price})
                position = 0
        # Close any open position at the end
        if position == 1:
            price = stock_data.iloc[-1]['Close']
            trades.append({'Date': stock_data.index[-1], 'Type': 'Sell', 'Price': price})
        return trades

    def calculate_returns(self, trades, stock_data):
        """
        Calculate cumulative returns based on executed trades.
        """
        returns = []
        buy_price = None
        for trade in trades:
            if trade['Type'] == 'Buy':
                buy_price = trade['Price']
            elif trade['Type'] == 'Sell' and buy_price is not None:
                sell_price = trade['Price']
                ret = (sell_price - buy_price) / buy_price
                returns.append(ret)
                buy_price = None
        cumulative_return = np.prod([1 + r for r in returns]) - 1 if returns else 0
        return cumulative_return, returns

    def backtest_crewai(self, stock_data, indicator_data):
        print("\nRunning CrewAI backtest...")
        bullish, bearish = self.run_crewai_system(stock_data, indicator_data)
        print(f"CrewAI Bullish Signals: {bullish}")
        print(f"CrewAI Bearish Signals: {bearish}")

        trades = self.simulate_trades(stock_data, bullish, bearish)
        print(f"CrewAI Trades: {trades}")

        cumulative_return, returns = self.calculate_returns(trades, stock_data)
        print(f"CrewAI Cumulative Return: {cumulative_return:.2%}")

        return cumulative_return, returns

    def backtest_non_crewai(self, stock_data, indicator_data):
        print("\nRunning non-CrewAI backtest...")
        bullish, bearish = self.run_non_crewai_system(stock_data, indicator_data)
        print(f"Non-CrewAI Bullish Signals: {bullish}")
        print(f"Non-CrewAI Bearish Signals: {bearish}")

        trades = self.simulate_trades(stock_data, bullish, bearish)
        print(f"Non-CrewAI Trades: {trades}")

        cumulative_return, returns = self.calculate_returns(trades, stock_data)
        print(f"Non-CrewAI Cumulative Return: {cumulative_return:.2%}")

        return cumulative_return, returns

    def compare_results(self, crewai_result, non_crewai_result):
        crewai_cum_ret, crewai_returns = crewai_result
        non_crewai_cum_ret, non_crewai_returns = non_crewai_result

        print("\nComparison Results:")
        print("-------------------")
        print(f"CrewAI Cumulative Return: {crewai_cum_ret:.2%}")
        print(f"Non-CrewAI Cumulative Return: {non_crewai_cum_ret:.2%}")

        if crewai_cum_ret > non_crewai_cum_ret:
            print("CrewAI system outperformed the non-CrewAI system.")
        elif crewai_cum_ret < non_crewai_cum_ret:
            print("Non-CrewAI system outperformed the CrewAI system.")
        else:
            print("Both systems performed equally.")

    def run_backtest(self):
        stock_data = self.fetch_stock_data()
        indicator_data = self.calculate_indicator(stock_data)

        # Backtest CrewAI system
        crewai_result = self.backtest_crewai(stock_data, indicator_data)

        # Backtest non-CrewAI system
        non_crewai_result = self.backtest_non_crewai(stock_data, indicator_data)

        # Compare results
        self.compare_results(crewai_result, non_crewai_result)

if __name__ == "__main__":
    print("### Divergence Trading Backtest ###")
    company = input("Enter the company ticker symbol (e.g., AAPL): ").upper()
    indicator_name = input("Enter the indicator for divergence detection (MACD/RSI): ").upper()

    if indicator_name not in ['MACD', 'RSI']:
        print("Invalid indicator. Please choose either 'MACD' or 'RSI'.")
        exit(1)

    backtester = Backtester(company, indicator_name)
    backtester.run_backtest()
