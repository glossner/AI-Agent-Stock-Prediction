import backtrader as bt
import pandas as pd
from dotenv import load_dotenv
import os
from src.Agents.MACD.macd_analysis_agent import MACDAnalysisAgent
from src.Indicators.macd import MACDIndicator
from crewai import Crew
from src.Data_Retrieval.data_fetcher import DataFetcher
from datetime import datetime
import sys

# Load environment variables
load_dotenv()


class MACDCrewAIStrategy(bt.Strategy):
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

        # Initialize MACD Indicator using the data_df
        macd = MACDIndicator(data_df)
        self.macd_data = macd.calculate_macd()

        # Set up CrewAI agent and task for analyzing MACD data
        macd_agent = MACDAnalysisAgent().macd_trading_advisor()
        macd_analysis_agent = MACDAnalysisAgent()
        self.macd_task = macd_analysis_agent.macd_analysis(macd_agent, self.macd_data)

        # Run CrewAI agent
        crew = Crew(
            agents=[macd_agent],
            tasks=[self.macd_task],
            verbose=True
        )
        self.crew_output = crew.kickoff()

    def next(self):
        # Fetch MACD and Signal Line values
        macd_value = self.macd_data['MACD'].iloc[-1]
        signal_value = self.macd_data['Signal_Line'].iloc[-1]
        close_price = self.dataclose[0]

        # Log current MACD and Signal Line values
        self.log(f'MACD: {macd_value:.2f}, Signal: {signal_value:.2f}, Close: {close_price:.2f}')

        # Buy if MACD crosses above Signal Line
        if macd_value > signal_value and not self.position:
            self.order = self.buy()
            self.log(f'BUY CREATE, {close_price:.2f}')

        # Sell if MACD crosses below Signal Line
        elif macd_value < signal_value and self.position:
            self.order = self.sell()
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


class MACDStrategy(bt.Strategy):
    params = dict(
        data_df=None,  # Add data_df as a parameter
        printlog=True,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

        # Use the data_df passed in via params
        data_df = self.params.data_df

        # Initialize MACD Indicator using the data_df
        macd = MACDIndicator(data_df)
        self.macd_data = macd.calculate_macd()

    def next(self):
        macd_value = self.macd_data['MACD'].iloc[-1]
        signal_value = self.macd_data['Signal_Line'].iloc[-1]
        close_price = self.dataclose[0]

        self.log(f'MACD: {macd_value:.2f}, Signal: {signal_value:.2f}, Close: {close_price:.2f}')

        # Buy if MACD crosses above Signal Line
        if macd_value > signal_value and not self.position:
            self.order = self.buy()
            self.log(f'BUY CREATE, {close_price:.2f}')

        # Sell if MACD crosses below Signal Line
        elif macd_value < signal_value and self.position:
            self.order = self.sell()
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
        open='Open',
        high='High',
        low='Low',
        close='Close',
        volume='Volume',
        openinterest=-1
    )
    cerebro.adddata(data)

    # Conditionally pass 'company' if the strategy supports it
    if 'company' in strategy_class.params._getkeys():
        cerebro.addstrategy(strategy_class, data_df=data_df, company=company, printlog=True)
    else:
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

    return {
        'strategy_name': strategy_name,
        'sharpe_ratio': sharpe.get('sharperatio', 'N/A'),
        'total_return': cumulative_return * 100,
        'annual_return': annual_return * 100,
        'max_drawdown': drawdown.max.drawdown,
    }


if __name__ == '__main__':
    company = 'AAPL'
    data_fetcher = DataFetcher(start_date=datetime(2015, 1, 1), end_date=datetime(2024, 10, 30))
    data_df = data_fetcher.get_stock_data(company)

    if data_df.empty:
        print(f"No price data found for {company}")
        sys.exit()

    # Fix MultiIndex columns
    if isinstance(data_df.columns, pd.MultiIndex):
        data_df.columns = [' '.join(col).strip() for col in data_df.columns.values]
        data_df.columns = [col.split(' ')[0] for col in data_df.columns]

    # Rename and filter columns for Backtrader
    data_df.rename(columns={
        'Adj Close': 'Close',
        'Close': 'Close',
        'Open': 'Open',
        'High': 'High',
        'Low': 'Low',
        'Volume': 'Volume'
    }, inplace=True)
    data_df = data_df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()

    # Run CrewAI MACD Strategy
    macd_metrics_crewai = run_strategy(MACDCrewAIStrategy, 'MACD CrewAI Strategy', data_df, company)

    # Run Non-CrewAI MACD Strategy
    macd_metrics_noncrewai = run_strategy(MACDStrategy, 'Non-CrewAI MACD Strategy', data_df)

    print("\nComparison of Strategies:")
    print("-------------------------")
    metrics = ['strategy_name', 'sharpe_ratio', 'total_return', 'annual_return', 'max_drawdown']
    df_metrics = pd.DataFrame([macd_metrics_crewai, macd_metrics_noncrewai], columns=metrics)
    print(df_metrics.to_string(index=False))

