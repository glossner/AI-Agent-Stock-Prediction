import backtrader as bt
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
import os
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks
from src.Indicators.fibonacci import FibonacciRetracement
from crewai import Crew
import sys

# Load environment variables
load_dotenv()

class FibonacciCrewAIStrategy(bt.Strategy):
    params = dict(
        company='AAPL',
        data_df=None,  # Add data_df as a parameter
        printlog=True,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

        # Use the data_df passed in via params
        data_df = self.params.data_df

        # Initialize Fibonacci Retracement levels using the data_df
        fibonacci = FibonacciRetracement(data_df)
        self.fib_levels = fibonacci.calculate_levels()

        # Set up CrewAI agent and task for analyzing Fibonacci levels
        agents = StockAnalysisAgents()
        tasks = StockAnalysisTasks()
        self.financial_analyst_agent = agents.financial_analyst()
        self.fibonacci_task = tasks.fibonacci_analysis(self.financial_analyst_agent, self.fib_levels)

        # Run CrewAI agent
        crew = Crew(
            agents=[self.financial_analyst_agent],
            tasks=[self.fibonacci_task],
            verbose=True
        )
        self.crew_output = crew.kickoff()

    def next(self):
        close_price = self.dataclose[0]
        if close_price <= self.fib_levels['61.8%'] and not self.position:
            self.order = self.buy()
            if self.params.printlog:
                self.log(f'BUY CREATE, {close_price:.2f}')

        elif close_price >= self.fib_levels['38.2%'] and self.position:
            self.order = self.sell()
            if self.params.printlog:
                self.log(f'SELL CREATE, {close_price:.2f}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}')

class FibonacciStrategy(bt.Strategy):
    params = dict(
        data_df=None,  # Add data_df as a parameter
        printlog=True,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

        # Use the data_df passed in via params
        data_df = self.params.data_df

        # Initialize Fibonacci Retracement levels using the data_df
        fibonacci = FibonacciRetracement(data_df)
        self.fib_levels = fibonacci.calculate_levels()

    def next(self):
        close_price = self.dataclose[0]
        if close_price <= self.fib_levels['61.8%'] and not self.position:
            self.order = self.buy()
            if self.params.printlog:
                self.log(f'BUY CREATE, {close_price:.2f}')

        elif close_price >= self.fib_levels['38.2%'] and self.position:
            self.order = self.sell()
            if self.params.printlog:
                self.log(f'SELL CREATE, {close_price:.2f}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}')

def run_strategy(strategy_class, strategy_name, data_df, company=None):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    # Create the data feed with adjusted column names
    data = bt.feeds.PandasData(
        dataname=data_df,
        datetime=None,  # Use index as datetime
        open='Open',
        high='High',
        low='Low',
        close='Close',
        volume='Volume',
        openinterest=-1
    )
    cerebro.adddata(data)

    # Modify this part to conditionally pass 'company'
    if company:
        # Strategy requires 'company' parameter
        cerebro.addstrategy(strategy_class, company=company, data_df=data_df, printlog=True)
    else:
        # Strategy does not require 'company' parameter
        cerebro.addstrategy(strategy_class, data_df=data_df, printlog=True)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, _name='timereturn')

    print(f'\nRunning {strategy_name}...')
    print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
    results = cerebro.run()
    strat = results[0]
    print(f'Final Portfolio Value: {cerebro.broker.getvalue():.2f}')

    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    timereturn = strat.analyzers.timereturn.get_analysis()

    strategy_returns = pd.Series(timereturn)
    cumulative_return = (strategy_returns + 1.0).prod() - 1.0
    start_date = data_df.index[0]
    end_date = data_df.index[-1]
    num_years = (end_date - start_date).days / 365.25
    annual_return = (1 + cumulative_return) ** (1 / num_years) - 1 if num_years != 0 else 0.0

    print(f'\n{strategy_name} Performance Metrics:')
    print('----------------------------------------')
    print(f"Sharpe Ratio: {sharpe.get('sharperatio', 'N/A')}")
    print(f"Total Return: {cumulative_return * 100:.2f}%")
    print(f"Annual Return: {annual_return * 100:.2f}%")
    print(f"Max Drawdown: {drawdown.max.drawdown:.2f}%")

    # Plot the strategy results (comment out if not needed)
    # cerebro.plot(style='candlestick')

    return {
        'strategy_name': strategy_name,
        'sharpe_ratio': sharpe.get('sharperatio', 'N/A'),
        'total_return': cumulative_return * 100,
        'annual_return': annual_return * 100,
        'max_drawdown': drawdown.max.drawdown,
    }

if __name__ == '__main__':
    company = 'AAPL'
    data_df = yf.download(company, start='2020-01-01', end='2024-10-30')

    if data_df.empty:
        print(f"No price data found for {company}")
        sys.exit()

    # Flatten the columns if they are MultiIndex
    if isinstance(data_df.columns, pd.MultiIndex):
        data_df.columns = [' '.join(col).strip() for col in data_df.columns.values]
        # Remove the ticker symbol from the column names
        data_df.columns = [col.split(' ')[0] for col in data_df.columns]

    # If you prefer to use 'Adj Close' as 'Close', rename it
    if 'Adj Close' in data_df.columns:
        data_df['Close'] = data_df['Adj Close']

    # Remove any unnecessary columns
    data_df = data_df[['Open', 'High', 'Low', 'Close', 'Volume']]

    # Run the CrewAI Fibonacci Strategy
    fib_metrics_crewai = run_strategy(
        FibonacciCrewAIStrategy,
        'Fibonacci CrewAI Strategy',
        data_df.copy(),
        company
    )

    # Run the Non-CrewAI Fibonacci Strategy
    fib_metrics_noncrewai = run_strategy(
        FibonacciStrategy,
        'Non-CrewAI Fibonacci Strategy',
        data_df.copy()
        # Do not pass 'company' here; it's optional and defaults to None
    )

    # Compare the performance metrics
    print("\nComparison of Strategies:")
    print("-------------------------")
    metrics = ['strategy_name', 'sharpe_ratio', 'total_return', 'annual_return', 'max_drawdown']
    df_metrics = pd.DataFrame([fib_metrics_crewai, fib_metrics_noncrewai], columns=metrics)
    print(df_metrics.to_string(index=False))
