import backtrader as bt
import yfinance as yf
import pandas as pd
from datetime import datetime
import os
import sys
from dotenv import load_dotenv
from src.Agents.Bollinger_agent.backtest_bollinger_agent import BollingerAnalysisAgents2
from src.Indicators.backtest_bollinger import BollingerBands
from src.Agents.Bollinger_agent.bollinger_agent import BollingerAnalysisAgents
from src.Indicators.bollinger import BollingerBands

# Load environment variables
load_dotenv()

class BollingerBandsStrategy(bt.Strategy):
    params = dict(
        period=20,          # Period for Bollinger Bands calculation
        devfactor=2.0,      # Standard deviation factor
        printlog=True       # Set to True if you want logs
    )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(self.data.close, period=self.params.period, devfactor=self.params.devfactor)
        self.order = None

    def next(self):
        if not self.position and self.data.close < self.boll.lines.bot:
            self.order = self.buy()
            if self.params.printlog:
                self.log(f"BUY CREATE: {self.data.close[0]:.2f}")

        elif self.position and self.data.close > self.boll.lines.top:
            self.order = self.sell()
            if self.params.printlog:
                self.log(f"SELL CREATE: {self.data.close[0]:.2f}")

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} {txt}")

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY EXECUTED: Price: {order.executed.price:.2f}")
            elif order.issell():
                self.log(f"SELL EXECUTED: Price: {order.executed.price:.2f}")
            self.bar_executed = len(self)
        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f"OPERATION PROFIT: GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}")

import time
from crewai import Crew

class CrewAIBollingerBandsStrategy(bt.Strategy):
    params = dict(
        period=20,
        devfactor=2.0,
        printlog=True
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.bollinger_agent = BollingerAnalysisAgents2()  # Instantiate BollingerAnalysisAgents
        self.investment_advisor_agent = self.bollinger_agent.bollinger_bands_investment_advisor()
        
        # Initialize Bollinger Bands indicator
        self.bollinger = bt.indicators.BollingerBands(self.dataclose, period=self.params.period, devfactor=self.params.devfactor)
        
        # Run CrewAI analysis once and store result
        self.analysis_result_text = self.run_crew_analysis()

    def run_crew_analysis(self):
        # This function does not access indicator values directly
        # Placeholder dictionary; actual values will be assigned in `next`
        dummy_bollinger_data = {
            "Upper Band": None,
            "Lower Band": None,
            "Moving Average": None
        }

        # Create the task with the dummy Bollinger Bands data
        task = self.bollinger_agent.bollinger_analysis(self.investment_advisor_agent, dummy_bollinger_data)

        # Execute the task with CrewAI
        crew = Crew(agents=[self.investment_advisor_agent], tasks=[task], verbose=True)
        result = crew.kickoff()

        # Extract the output text from the result
        return result.output if hasattr(result, 'output') else "No response"

    def next(self):
        # Access the latest Bollinger Bands values at each step
        bollinger_data = {
            "Upper Band": self.bollinger.lines.top[0],
            "Lower Band": self.bollinger.lines.bot[0],
            "Moving Average": self.bollinger.lines.mid[0]
        }

        # Use the analysis result from CrewAI to decide on trading actions
        if "buy" in self.analysis_result_text.lower() and not self.position:
            self.order = self.buy()
            if self.params.printlog:
                self.log(f"CREW AI BUY CREATE: {self.dataclose[0]:.2f}")

        elif "sell" in self.analysis_result_text.lower() and self.position:
            self.order = self.sell()
            if self.params.printlog:
                self.log(f"CREW AI SELL CREATE: {self.dataclose[0]:.2f}")

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} {txt}")

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY EXECUTED: Price: {order.executed.price:.2f}")
            elif order.issell():
                self.log(f"SELL EXECUTED: Price: {order.executed.price:.2f}")
            self.bar_executed = len(self)
        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f"OPERATION PROFIT: GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}")








def run_backtest(strategy_class, strategy_name, data_df):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)
    
    cerebro.addstrategy(strategy_class)
    
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, _name='timereturn')
    
    print(f"\nRunning {strategy_name}...")
    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
    results = cerebro.run()
    strat = results[0]
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")

    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    timereturn = strat.analyzers.timereturn.get_analysis()
    
    strategy_returns = pd.Series(timereturn)
    cumulative_return = (strategy_returns + 1.0).prod() - 1.0
    
    start_date = data_df.index[0]
    end_date = data_df.index[-1]
    num_years = (end_date - start_date).days / 365.25
    annual_return = (1 + cumulative_return) ** (1 / num_years) - 1 if num_years != 0 else 0.0

    print(f"\n{strategy_name} Performance Metrics:")
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
    company = 'AAPL'
    data_df = yf.download(company, start='2020-01-01', end='2024-10-30')
    if data_df.empty:
        print(f"No data found for {company}")
        sys.exit()
    
    normal_metrics = run_backtest(BollingerBandsStrategy, 'Normal Bollinger Bands Strategy', data_df)
    crew_ai_metrics = run_backtest(CrewAIBollingerBandsStrategy, 'Crew AI Bollinger Bands Strategy', data_df)
    
    print("\nComparison of Strategies:")
    print(f"Normal Strategy Metrics: {normal_metrics}")
    print(f"CrewAI Strategy Metrics: {crew_ai_metrics}")
