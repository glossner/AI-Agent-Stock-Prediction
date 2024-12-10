import backtrader as bt
from datetime import datetime
import pandas as pd
import yfinance as yf
import sys
import os
from dotenv import load_dotenv
from crewai import Crew

# Load environment variables (e.g., API keys)
load_dotenv()

# Import necessary components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.Agents.divergence_agents.divergence_agent import DivergenceAnalysisAgents, DivergenceAnalysisTasks
from src.Indicators.macd_indicator import MACDIndicator
from src.Indicators.rsi_divergence import RSIIndicator
from src.Data_Retrieval.data_fetcher import DataFetcher

class ReversalTradingSystem(bt.Strategy):
    params = dict(
        company='AAPL',
        indicator_name='MACD',  # Could also be 'RSI'
        printlog=False,
    )

    def __init__(self):
        # Set up close data and order tracker
        self.dataclose = self.datas[0].close
        self.order = None
        self.company = self.params.company
        self.indicator_name = self.params.indicator_name

        # Initialize divergence analysis agents and tasks
        divergence_agents = DivergenceAnalysisAgents()
        divergence_tasks = DivergenceAnalysisTasks()
        self.divergence_agent = divergence_agents.divergence_trading_advisor()

        # Fetch stock data for the specified company
        data_fetcher = DataFetcher()
        stock_data = data_fetcher.get_stock_data(self.company)

        # Calculate MACD or RSI indicator data
        if self.indicator_name == 'MACD':
            indicator_data = MACDIndicator().calculate(stock_data)
        elif self.indicator_name == 'RSI':
            indicator_data = RSIIndicator().calculate(stock_data)
        else:
            raise ValueError("Indicator name must be 'MACD' or 'RSI'.")

        # Detect divergence signals and create task
        divergence_task = divergence_tasks.detect_divergence(self.divergence_agent, stock_data, indicator_data, self.indicator_name)
        self.crew_output = self.run_divergence_analysis(divergence_task)

        # Parse divergence signals
        self.bullish_dates, self.bearish_dates = self.parse_divergence_signals(self.crew_output)

    def run_divergence_analysis(self, divergence_task):
        # Kick off the CrewAI agent with the task
        crew = Crew(
            agents=[self.divergence_agent],
            tasks=[divergence_task],
            verbose=True
        )
        return crew.kickoff()

    def parse_divergence_signals(self, crew_output):
        # Example function to parse bullish and bearish divergence dates from crew_output
        bullish_dates = []
        bearish_dates = []

        if hasattr(crew_output, 'tasks_output') and crew_output.tasks_output:
            task_output = crew_output.tasks_output[0]
            if hasattr(task_output, 'content'):
                # Assuming content has lists of dates in some format, parse accordingly
                bullish_dates = [date.strip() for date in task_output.content.get('Bullish Divergences', [])]
                bearish_dates = [date.strip() for date in task_output.content.get('Bearish Divergences', [])]
        
        return bullish_dates, bearish_dates

    def next(self):
        current_date = self.datas[0].datetime.date(0)
        
        # Execute a buy order if there’s a bullish divergence on the current date
        if str(current_date) in self.bullish_dates and not self.position:
            cash = self.broker.getcash()
            price = self.dataclose[0]
            size = (cash * 0.9) // price  # Use 90% of available cash
            self.order = self.buy(size=size)
            if self.params.printlog:
                self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')
        
        # Execute a sell order if there’s a bearish divergence on the current date
        elif str(current_date) in self.bearish_dates and self.position:
            self.order = self.sell(size=self.position.size)
            if self.params.printlog:
                self.log(f'SELL CREATE, {self.dataclose[0]:.2f}')

    def log(self, txt, dt=None):
        ''' Logging function '''
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
            self.bar_executed = len(self)
        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}')


class BuyAndHoldStrategy(bt.Strategy):
    params = dict(
        allocation=1.0,  # Allocate 100% of available cash for buy-and-hold
        printlog=False,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

    def next(self):
        if not self.position:
            cash = self.broker.getcash()
            price = self.dataclose[0]
            size = (cash * self.params.allocation) // price
            self.order = self.buy(size=size)
            if self.params.printlog:
                self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')

    def log(self, txt, dt=None):
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

def run_reversal_backtest(company='AAPL', indicator='MACD', start='2020-01-01', end='2024-10-30'):
    # Fetch historical price data using yfinance
    data_df = yf.download(company, start=start, end=end)
    if data_df.empty:
        print(f"No price data found for {company}")
        return
    
    # Initialize cerebro and set initial cash
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    # Load data into cerebro
    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)

    # Run both ReversalTradingSystem and BuyAndHoldStrategy
    cerebro.addstrategy(ReversalTradingSystem, company=company, indicator_name=indicator, printlog=True)
    cerebro.addstrategy(BuyAndHoldStrategy, printlog=True)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, _name='timereturn')

    # Run backtest
    print(f'\nRunning Reversal Trading System and Buy-and-Hold Backtest for {company}...')
    results = cerebro.run()

    # Display results for both strategies
    for strat, strategy_name in zip(results, ["Reversal Trading System", "Buy-and-Hold Strategy"]):
        print(f'\n{strategy_name} Performance Metrics:')
        print('----------------------------------------')
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        timereturn = strat.analyzers.timereturn.get_analysis()

        strategy_returns = pd.Series(timereturn)
        cumulative_return = (strategy_returns + 1.0).prod() - 1.0
        start_date = data_df.index[0]
        end_date = data_df.index[-1]
        num_years = (end_date - start_date).days / 365.25
        annual_return = (1 + cumulative_return) ** (1 / num_years) - 1 if num_years else 0.0

        print(f"Sharpe Ratio: {sharpe.get('sharperatio', 'N/A')}")
        print(f"Total Return: {cumulative_return * 100:.2f}%")
        print(f"Annual Return: {annual_return * 100:.2f}%")
        print(f"Max Drawdown: {drawdown.max.drawdown:.2f}%")

    # Plot the strategy results
    cerebro.plot(style='candlestick')

# Run the backtest
if __name__ == '__main__':
    run_reversal_backtest()
