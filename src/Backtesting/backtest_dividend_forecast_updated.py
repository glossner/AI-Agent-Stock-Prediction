import backtrader as bt
from datetime import datetime
import pandas as pd
import numpy as np
from yahooquery import Ticker
import os
import sys
from dotenv import load_dotenv
import yfinance as yf  # Import yfinance for data fetching
import re

# Load environment variables (e.g., API keys)
load_dotenv()

# Import CrewAI components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from crewai import Crew
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks

class FinancialCrew:
    def __init__(self, company):
        self.company = company

    def run(self):
        agents = StockAnalysisAgents()
        tasks = StockAnalysisTasks()

        # Create the dividend forecasting agent with the company name
        dividend_forecasting_agent = agents.dividend_forecasting_agent(self.company)

        # Fetch financial data for the company using yahooquery
        financial_data = self.fetch_financial_data()

        # Create the dividend forecasting task with the company name
        dividend_forecasting_task = tasks.forecast_dividend_growth(dividend_forecasting_agent, financial_data, self.company)

        # Kickoff the CrewAI with the agent and task
        crew = Crew(
            agents=[dividend_forecasting_agent],
            tasks=[dividend_forecasting_task],
            verbose=False  # Set to True if you want detailed logs
        )

        result = crew.kickoff()
        return result  # This should be the forecast text

    def fetch_financial_data(self):
        # Fetch financial data using yahooquery
        print(f"Fetching financial data for {self.company}...")
        ticker = Ticker(self.company)
        income_statement = ticker.income_statement(frequency='a')  # Get annual income statement
        cash_flow_statement = ticker.cash_flow(frequency='a')  # Get annual cash flow statement

        # Convert data to strings for easier analysis
        return {
            "IncomeStatement": income_statement.to_string(),
            "CashFlowStatement": cash_flow_statement.to_string()
        }

class CrewAIStrategy(bt.Strategy):
    params = dict(
        company='AAPL',
        printlog=False,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

        # Fetch financial data and get dividend forecast using CrewAI
        self.financial_crew = FinancialCrew(self.params.company)
        crew_output = self.financial_crew.run()

        # Extract the forecast text from the CrewOutput object
        if hasattr(crew_output, 'tasks_output') and crew_output.tasks_output:
            # Assuming tasks_output is a list of task outputs
            task_output = crew_output.tasks_output[0]
            if hasattr(task_output, 'content'):
                self.dividend_forecast_text = task_output.content
            else:
                print("Warning: Task output does not have 'content' attribute.")
                self.dividend_forecast_text = str(task_output)
        else:
            print("Warning: 'tasks_output' is not available or empty in crew_output.")
            self.dividend_forecast_text = str(crew_output)

        # Parse the forecasted growth rate
        self.forecasted_growth_rate = self.parse_dividend_growth(self.dividend_forecast_text)

    def parse_dividend_growth(self, forecast_text):
        # Remove markdown formatting (asterisks, underscores)
        clean_text = re.sub(r'[\*\_]', '', forecast_text)
        
        # Find all occurrences of percentages in the forecast section
        matches = re.findall(r'Year\s*\d+:\s*(\d+(\.\d+)?)%\s*increase', clean_text, re.IGNORECASE)
        if matches:
            # Extract the percentages and calculate the average growth rate
            growth_rates = [float(match[0]) for match in matches]
            average_growth_rate = sum(growth_rates) / len(growth_rates) / 100  # Convert to decimal
            print(f"Parsed average dividend growth rate: {average_growth_rate:.4f}")
            return average_growth_rate
        else:
            print("Could not parse dividend growth rates from CrewAI output.")
            return 0.0  # Default if not found

    def next(self):
        # Buy once if forecasted average dividend growth is above a threshold and no position is held
        if self.forecasted_growth_rate > 0.05 and not self.position:
            cash = self.broker.getcash()  # Available cash in the portfolio
            price = self.data.close[0]  # Current close price of the asset
            size = (cash * 1.0) // price  # Allocate 100% of cash for buy-and-hold
            self.order = self.buy(size=size)  # Place a single buy order

            if self.params.printlog:
                self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')

    def log(self, txt, dt=None):
        '''Logging function'''
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            self.bar_executed = len(self)
        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}')


class NonCrewAIStrategy(bt.Strategy):
    params = dict(
        allocation=1.0,  # Allocate 100% of available cash for the buy-and-hold strategy
        printlog=False,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

    def next(self):
        # Execute buy order only once
        if not self.position:  # Check if there is no current position (i.e., no stocks held)
            cash = self.broker.getcash()  # Available cash in the portfolio
            price = self.data.close[0]  # Current close price of the asset
            size = (cash * self.params.allocation) // price  # Calculate size based on allocation
            self.order = self.buy(size=size)  # Place a buy order for the calculated size

            if self.params.printlog:
                self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')

    def log(self, txt, dt=None):
        '''Logging function'''
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            self.bar_executed = len(self)
        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}')


def run_strategy(strategy_class, strategy_name, data_df, company=None):
    # Initialize cerebro
    cerebro = bt.Cerebro()
    
    # Set initial cash
    cerebro.broker.setcash(100000.0)
    
    # Set commission (e.g., 0.1% per trade)
    cerebro.broker.setcommission(commission=0.001)
    
    # Create a Data Feed
    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)
    
    # Add the strategy, passing 'company' only if needed
    if company:
        cerebro.addstrategy(strategy_class, company=company, printlog=True)
    else:
        cerebro.addstrategy(strategy_class, printlog=True)
    
    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, _name='timereturn')
    
    # Run backtest
    print(f'\nRunning {strategy_name}...')
    print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
    results = cerebro.run()
    strat = results[0]
    print(f'Final Portfolio Value: {cerebro.broker.getvalue():.2f}')
    
    # Get performance metrics
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    timereturn = strat.analyzers.timereturn.get_analysis()
    
    # Convert the TimeReturn analyzer output to a pandas Series
    strategy_returns = pd.Series(timereturn)
    
    # Calculate cumulative return
    cumulative_return = (strategy_returns + 1.0).prod() - 1.0
    
    # Calculate annualized return
    start_date = data_df.index[0]
    end_date = data_df.index[-1]
    num_years = (end_date - start_date).days / 365.25
    
    if num_years == 0:
        print("num_years is zero, cannot calculate annual_return.")
        annual_return = 0.0
    else:
        annual_return = (1 + cumulative_return) ** (1 / num_years) - 1
    
    print(f'\n{strategy_name} Performance Metrics:')
    print('----------------------------------------')
    print(f"Sharpe Ratio: {sharpe.get('sharperatio', 'N/A')}")
    print(f"Total Return: {cumulative_return * 100:.2f}%")
    print(f"Annual Return: {annual_return * 100:.2f}%")
    print(f"Max Drawdown: {drawdown.max.drawdown:.2f}%")

    # Plot the strategy results
    cerebro.plot(style='candlestick')  # 'style' can be 'candlestick' or 'line'
    
    # Return metrics if needed
    return {
        'strategy_name': strategy_name,
        'sharpe_ratio': sharpe.get('sharperatio', 'N/A'),
        'total_return': cumulative_return * 100,
        'annual_return': annual_return * 100,
        'max_drawdown': drawdown.max.drawdown,
    }


if __name__ == '__main__':
    # Define the company to analyze
    company = 'AAPL'  # Or prompt the user for input
    
    # Fetch historical price data using yfinance
    data_df = yf.download(company, start='2020-01-01', end='2024-10-30')
    if data_df.empty:
        print(f"No price data found for {company}")
        sys.exit()
    
    # Run CrewAIStrategy
    crewai_metrics = run_strategy(CrewAIStrategy, 'CrewAI Strategy', data_df, company)
    
    # Run NonCrewAIStrategy
    noncrewai_metrics = run_strategy(NonCrewAIStrategy, 'Buy and Hold', data_df)

