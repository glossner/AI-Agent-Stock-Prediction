import backtrader as bt
import pandas as pd
import yfinance as yf
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Load environment variables (e.g., API keys)
load_dotenv()

# Import CrewAI components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from crewai import Crew
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks


class SectorRotationCrew:
    def __init__(self):
        self.agent = StockAnalysisAgents().economic_forecasting_agent()

    def run(self, combined_data):
        # Create sector prediction task with macroeconomic and policy data
        task = StockAnalysisTasks().predict_sector_performance(self.agent, combined_data)
        crew = Crew(agents=[self.agent], tasks=[task], verbose=True)
        return crew.kickoff()


class CrewAISectorRotationStrategy(bt.Strategy):
    params = dict(
        sectors=['Technology', 'Healthcare', 'Finance'],
        printlog=False,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.combined_data = {
            "MacroeconomicData": "Mock data for GDP, inflation, etc.",
            "FinancialReports": "Mock financial reports",
            "PolicyChanges": "Mock policy changes",
        }

        # Initialize CrewAI to get sector predictions
        self.sector_crew = SectorRotationCrew()
        crew_output = self.sector_crew.run(self.combined_data)
        self.predicted_sectors = self.parse_sectors(crew_output)

    def parse_sectors(self, crew_output):
        # Mock parsing function for demonstration
        return ["Technology", "Healthcare"]

    def next(self):
        if set(self.predicted_sectors) != set(self.params.sectors):
            if not self.position:
                cash = self.broker.getcash()
                price = self.data.close[0]
                size = (cash * 0.5) // price
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


class BuyAndHold(bt.Strategy):
    params = dict(
        allocation=1.0,
    )

    def __init__(self):
        pass

    def next(self):
        current_date = self.datas[0].datetime.date(0)
        if not self.position:
            cash = self.broker.getcash()
            price = self.data.close[0]
            size = (cash * self.params.allocation) // price
            self.buy(size=size)
            logging.info(f"{current_date}: BUY {size} shares at {price:.2f}")


def run_strategy(strategy_class, strategy_name, data_df):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)

    # Conditionally add printlog parameter only if the strategy expects it
    if strategy_class == CrewAISectorRotationStrategy:
        cerebro.addstrategy(strategy_class, printlog=True)
    else:
        cerebro.addstrategy(strategy_class)

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
    annual_return = (1 + cumulative_return) ** (1 / num_years) - 1 if num_years else 0.0

    print(f'\n{strategy_name} Performance Metrics:')
    print('----------------------------------------')
    print(f"Sharpe Ratio: {sharpe.get('sharperatio', 'N/A')}")
    print(f"Total Return: {cumulative_return * 100:.2f}%")
    print(f"Annual Return: {annual_return * 100:.2f}%")
    print(f"Max Drawdown: {drawdown.max.drawdown:.2f}%")

    cerebro.plot(style='candlestick')
    return {
        'strategy_name': strategy_name,
        'sharpe_ratio': sharpe.get('sharperatio', 'N/A'),
        'total_return': cumulative_return * 100,
        'annual_return': annual_return * 100,
        'max_drawdown': drawdown.max.drawdown,
    }


if __name__ == '__main__':
    data_df = yf.download("XLK", start='2020-01-01', end='2024-10-30')
    if data_df.empty:
        print("No price data found.")
        sys.exit()

    print("*********************************************")
    print("************* CrewAI Sector Rotation Strategy *********************")
    print("*********************************************")
    crewai_metrics = run_strategy(CrewAISectorRotationStrategy, 'CrewAI Sector Rotation Strategy', data_df)

    print("*********************************************")
    print("************* BUY AND HOLD ******************")
    print("*********************************************")
    buy_and_hold_metrics = run_strategy(BuyAndHold, 'Buy and Hold', data_df)
