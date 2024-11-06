import backtrader as bt
from datetime import datetime
import pandas as pd
import yfinance as yf
import logging
from crewai import Crew
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents  # Correct import for StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks    # Correct import for StockAnalysisTasks
from src.UI.sentiment_analysis import SentimentCrew 

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class SentimentCrew:
    def __init__(self, stock_or_sector):
        self.stock_or_sector = stock_or_sector

    def run(self):
        agents = StockAnalysisAgents()
        tasks = StockAnalysisTasks()

        # Initialize a sentiment analysis agent and task
        sentiment_agent = agents.sentiment_analyst()
        sentiment_task = tasks.analyze_sentiment(sentiment_agent, self.stock_or_sector)

        # Set up CrewAI and run the sentiment analysis
        crew = Crew(
            agents=[sentiment_agent],
            tasks=[sentiment_task],
            verbose=False
        )

        result = crew.kickoff()
        return result  # Expected to return a sentiment score or buy/sell decision

class SentimentBasedStrategy(bt.Strategy):
    params = dict(
        stock='AAPL',
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

        # Run sentiment analysis only once during initialization
        self.sentiment_crew = SentimentCrew(self.params.stock)
        sentiment_output = self.sentiment_crew.run()

        # Process sentiment output and decide on trading action
        self.sentiment_decision = self.parse_sentiment(sentiment_output)

        # Log the initial sentiment decision for clarity
        print(f"Initial Sentiment Decision: {self.sentiment_decision}")

    def parse_sentiment(self, sentiment_output):
        try:
            # Access the sentiment text
            if hasattr(sentiment_output, 'tasks_output') and sentiment_output.tasks_output:
                task_output = sentiment_output.tasks_output[0]
                
                # Check if there is a sentiment summary or description
                sentiment_text = ""
                if hasattr(task_output, 'summary'):
                    sentiment_text = task_output.summary.lower()
                elif hasattr(task_output, 'description'):
                    sentiment_text = task_output.description.lower()
                
                # Basic keyword search in sentiment text
                if 'buy' in sentiment_text or 'positive' in sentiment_text or 'stability' in sentiment_text:
                    return 'buy'
                elif 'sell' in sentiment_text or 'negative' in sentiment_text or 'caution' in sentiment_text:
                    return 'sell'
                else:
                    # If sentiment score is present, decide based on threshold
                    if 'score' in sentiment_text:
                        score = float(sentiment_text.split("score")[1].strip().split()[0])
                        if score > 0.3:  # Threshold for positive sentiment
                            return 'buy'
                        elif score < -0.3:  # Threshold for negative sentiment
                            return 'sell'
                    return 'hold'
            else:
                print("Warning: Sentiment output 'tasks_output' is unavailable or empty.")
                return 'hold'
        except Exception as e:
            print("Error parsing sentiment output:", e)
            return 'hold'

    def next(self):
        # Trade based on stored sentiment decision
        if not self.position and self.sentiment_decision == 'buy':
            cash = self.broker.getcash()
            size = int((cash * 1.0) // self.dataclose[0])
            self.order = self.buy(size=size)
            self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')

        elif self.position and self.sentiment_decision == 'sell':
            self.order = self.sell(size=self.position.size)
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
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

    def next(self):
        if not self.position:
            cash = self.broker.getcash()
            size = int(cash // self.dataclose[0])
            self.buy(size=size)
            self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')


def run_strategy(strategy_class, strategy_name, data_df, stock=None):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)
    
    if stock and strategy_class == SentimentBasedStrategy:
        cerebro.addstrategy(strategy_class, stock=stock)
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

    num_years = (data_df.index[-1] - data_df.index[0]).days / 365.25
    annual_return = (1 + cumulative_return) ** (1 / num_years) - 1 if num_years != 0 else 0.0

    print(f'\n{strategy_name} Performance Metrics:')
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
    
    crewai_metrics = run_strategy(SentimentBasedStrategy, 'Sentiment-Based Strategy', data_df, stock)
    buyhold_metrics = run_strategy(BuyAndHold, 'Buy and Hold Strategy', data_df)
