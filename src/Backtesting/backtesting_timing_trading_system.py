from datetime import datetime
import logging
import backtrader as bt
import yfinance as yf
from src.Data_Retrieval.timing_trading_data_fetcher import DataFetcher


# Strategy class for timing trading based on earnings date
class TimingTradingStrategy(bt.Strategy):
    params = (('allocation', 1.0),)  # Allocation of cash for each trade

    def __init__(self, stock, earnings_date):
        self.stock = stock
        self.earnings_date = datetime.strptime(earnings_date, '%Y-%m-%d') if isinstance(earnings_date, str) else earnings_date
        self.in_earnings_window = False  # Track if within earnings window

    def next(self):
        current_date = self.datas[0].datetime.date(0)
        self.in_earnings_window = (self.earnings_date.date() - current_date).days <= 5

        if self.in_earnings_window and not self.position:
            cash = self.broker.getcash()
            price = self.data.close[0]
            size = (cash * self.params.allocation) // price
            self.buy(size=size)
            logging.info(f"{current_date}: BUY {size} shares at {price:.2f} due to upcoming earnings on {self.earnings_date.date()}")

        elif not self.in_earnings_window and self.position:
            self.sell(size=self.position.size)
            price = self.data.close[0]
            logging.info(f"{current_date}: SELL {self.position.size} shares at {price:.2f} after earnings release")

# Backtesting function with performance metrics
def run_backtest(strategy_class, stock, data_feed, earnings_date, cash=10000, commission=0.001):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy_class, stock=stock, earnings_date=earnings_date)
    cerebro.adddata(data_feed)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission)

    # Add analyzers for performance metrics
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.01)
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    result = cerebro.run()
    strat = result[0]

    # Print performance metrics
    sharpe = strat.analyzers.sharpe.get_analysis()
    returns = strat.analyzers.returns.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    trades = strat.analyzers.trades.get_analysis()

    print("\nPerformance Metrics:")
    print(f"Sharpe Ratio: {sharpe.get('sharperatio', 'N/A')}")
    print(f"Total Return: {returns['rtot']*100:.2f}%")
    print(f"Average Daily Return: {returns['ravg']*100:.2f}%")
    print(f"Max Drawdown: {drawdown.drawdown*100:.2f}%")
    print(f"Max Drawdown Duration: {drawdown.get('maxdrawdownperiod', 'N/A')} days")
    print(f"Total Trades: {trades.total.total if 'total' in trades.total else 'N/A'}")
    print(f"Winning Trades: {trades.won.total if 'won' in trades else 'N/A'}")
    print(f"Losing Trades: {trades.lost.total if 'lost' in trades else 'N/A'}")
    print(f"Net Profit: {returns['rtot'] * 100:.2f}%")

    cerebro.plot()

# Main script to execute the backtest
if __name__ == '__main__':
    stock = 'AAPL'  # Replace with your stock ticker
    start = datetime(2010, 1, 1)
    end = datetime.today()

    # Fetch historical stock data
    data_fetcher = DataFetcher()
    earnings_date = data_fetcher.get_earnings_date(stock)
    print(f"Earnings Date: {earnings_date}")

    yfinance_fetcher = yf.Ticker(stock)
    data = yfinance_fetcher.history(start=start, end=end)
    if data.empty:
        print("No data retrieved for the given stock and date range.")
    else:
        # Convert pandas DataFrame to Backtrader data feed
        data_feed = bt.feeds.PandasData(dataname=data, fromdate=start, todate=end)

        print("*********************************************")
        print("************* Timing Trading Strategy *******")
        print("*********************************************")
        run_backtest(TimingTradingStrategy, stock, data_feed, earnings_date, cash=10000, commission=0.001)