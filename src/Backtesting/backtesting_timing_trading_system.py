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

