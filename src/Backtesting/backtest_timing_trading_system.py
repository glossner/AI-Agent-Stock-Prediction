import backtrader as bt
from datetime import datetime
import pandas as pd
import yfinance as yf
import logging
import os
from dotenv import load_dotenv

# Load environment variables (e.g., for API keys if needed)
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)


class TimingTradingSystemStrategy(bt.Strategy):
    params = dict(
        stock='AAPL',
        printlog=False,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.stock = self.params.stock
        self.decision = None

    def fetch_earnings_date(self):
        # Simulate fetching earnings dates
        return datetime(2024, 10, 31)  # Example fixed date

    def analyze_sentiment(self, earnings_date):
        # Placeholder for sentiment analysis around the earnings date
        if earnings_date and (earnings_date - datetime.now()).days <= 5:
            return "buy"
        else:
            return "sell"

    def next(self):
        # Run sentiment analysis logic to get buy/sell decision
        if not self.position:
            earnings_date = self.fetch_earnings_date()
            self.decision = self.analyze_sentiment(earnings_date)

            # Execute buy or sell decision
            if self.decision == 'buy':
                cash = self.broker.getcash()
                size = cash // self.dataclose[0]
                self.order = self.buy(size=size)
                if self.params.printlog:
                    self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')
            elif self.decision == 'sell' and self.position:
                self.order = self.sell(size=self.position.size)
                if self.params.printlog:
                    self.log(f'SELL CREATE, {self.dataclose[0]:.2f}')

    def log(self, txt, dt=None):
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


class BuyAndHold(bt.Strategy):
    params = (
        ('allocation', 1.0),  # Allocate 100% of available cash to buy and hold
    )

    def __init__(self):
        pass  # No indicators needed for Buy-and-Hold

    def next(self):
        current_date = self.datas[0].datetime.date(0)
        # Buy once and hold
        if not self.position:
            cash = self.broker.getcash()  # Get available cash
            price = self.data.close[0]  # Current price
            size = (cash * self.params.allocation) // price  # Calculate size to buy
            self.buy(size=size)  # Execute buy order
            logging.info(f"{current_date}: BUY {size} shares at {price:.2f}")


def run_strategy(strategy_class, strategy_name, data_df, stock=None):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)
    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)
    
    if strategy_class == TimingTradingSystemStrategy:
        cerebro.addstrategy(strategy_class, stock=stock, printlog=True)
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
    stock = 'AAPL'
    data_df = yf.download(stock, start='2020-01-01', end='2024-10-30')
    if data_df.empty:
        print(f"No price data found for {stock}")
        sys.exit()
    
    # Run TimingTradingSystemStrategy
    timing_trading_system_metrics = run_strategy(TimingTradingSystemStrategy, 'Timing Trading System Strategy', data_df, stock)
    
    # Run BuyAndHold Strategy
    buy_and_hold_metrics = run_strategy(BuyAndHold, 'Buy and Hold Strategy', data_df)

    # Print comparison of performance metrics
    print("\nPerformance Comparison:")
    print("----------------------------------------")
    for key in timing_trading_system_metrics:
        if key != 'strategy_name':
            print(f"{key.capitalize()} Comparison:")
            print(f"  {timing_trading_system_metrics['strategy_name']}: {timing_trading_system_metrics[key]}")
            print(f"  {buy_and_hold_metrics['strategy_name']}: {buy_and_hold_metrics[key]}")
            print()
