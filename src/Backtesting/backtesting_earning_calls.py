import backtrader as bt
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
import os
from src.Agents.Earnings_Calls_Sec_Filings_Agents.earnings_sec_analysis_agents import EarningsSecAnalysisAgents
from crewai import Crew
import sys
import requests

# Load environment variables
load_dotenv()

class CrewAIEarningsCallsStrategy(bt.Strategy):
    params = dict(
        company='AAPL',
        exchange='NASDAQ',
        data_df=None,
        printlog=True,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

        # Initialize Earnings Calls and SEC Filings Agents and Tasks
        self.sec_earnings_agents = EarningsSecAnalysisAgents()
        self.financial_analyst_agent = self.sec_earnings_agents.financial_analyst()

        # Fetch earnings call dates
        self.fetch_earnings_calls()

        # Initialize crew output
        self.crew_output = {}

    def fetch_sec_filings(self):
        from yahooquery import Ticker
        ticker = Ticker(self.params.company)
        sec_filings = ticker.sec_filings
        if sec_filings.empty:
            print("No SEC filings found for the company.")
            return None
        return sec_filings.to_json()

    def fetch_earnings_calls(self):
        url = f'https://v2.api.earningscall.biz/events?apikey={os.getenv("EARNINGSCAST_API_KEY")}&exchange={self.params.exchange}&symbol={self.params.company}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("API Response:", data)  # Debugging line
            events = data.get('events', [])
            if not events:
                print("No earnings events found.")
                self.earnings_call_dates = []
                self.earnings_data = None
                return
            # Extract dates
            event_dates = [event['date'] for event in events]
            self.earnings_call_dates = pd.to_datetime(event_dates).date
            self.earnings_data = events
        else:
            print("Error fetching earnings calls:", response.status_code)
            self.earnings_call_dates = []
            self.earnings_data = None

    def perform_crewai_analysis(self):
        sec_data = self.fetch_sec_filings()
        earnings_data = self.earnings_data

        if not sec_data and not earnings_data:
            print("No data available for analysis.")
            return

        # Re-initialize tasks
        self.sec_filings_task = self.sec_earnings_agents.analyze_sec_filings(
            self.financial_analyst_agent, sec_data)
        self.earnings_call_task = self.sec_earnings_agents.analyze_earnings_calls(
            self.financial_analyst_agent, earnings_data)

        # Re-run CrewAI agents
        crew = Crew(
            agents=[self.financial_analyst_agent],
            tasks=[self.sec_filings_task, self.earnings_call_task],
            verbose=True
        )
        self.crew_output = crew.kickoff()

    def get_recommendation_from_crew_output(self):
        # Simple keyword-based sentiment analysis
        analysis_text = ''
        for key in self.crew_output:
            analysis_text += self.crew_output[key]

        analysis_text = analysis_text.lower()

        if 'buy' in analysis_text or 'strong growth' in analysis_text or 'positive outlook' in analysis_text:
            return 'buy'
        elif 'sell' in analysis_text or 'decline' in analysis_text or 'negative outlook' in analysis_text:
            return 'sell'
        else:
            return 'hold'

    def next(self):
        current_date = self.datas[0].datetime.date(0)

        if current_date in self.earnings_call_dates:
            self.perform_crewai_analysis()

        # Get recommendation
        recommendation = self.get_recommendation_from_crew_output()

        # Make trading decisions based on the new analysis
        close_price = self.dataclose[0]
        if recommendation == 'buy' and not self.position:
            self.order = self.buy()
            if self.params.printlog:
                self.log(f'BUY CREATE, {close_price:.2f}')
        elif recommendation == 'sell' and self.position:
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



def run_strategy(strategy_class, strategy_name, data_df, company=None, exchange=None):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    data = bt.feeds.PandasData(
        dataname=data_df,
        datetime=None,
        open='Open',
        high='High',
        low='Low',
        close='Close',
        volume='Volume',
        openinterest=-1
    )
    cerebro.adddata(data)

    if company:
        cerebro.addstrategy(strategy_class, company=company, exchange=exchange, data_df=data_df, printlog=True)
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
    exchange = 'NASDAQ'
    data_df = yf.download(company, start='2020-01-01', end='2024-10-30')

    if data_df.empty:
        print(f"No price data found for {company}")
        sys.exit()

    if isinstance(data_df.columns, pd.MultiIndex):
        data_df.columns = [' '.join(col).strip() for col in data_df.columns.values]
        data_df.columns = [col.split(' ')[0] for col in data_df.columns]

    if 'Adj Close' in data_df.columns:
        data_df['Close'] = data_df['Adj Close']
    data_df = data_df[['Open', 'High', 'Low', 'Close', 'Volume']]

    metrics_crewai = run_strategy(
        CrewAIEarningsCallsStrategy,
        'CrewAI Earnings Calls Strategy',
        data_df.copy(),
        company,
        exchange
    )
    print(metrics_crewai)
