import backtrader as bt
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
import os
from crewai import Crew
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks
from yahooquery import Ticker
import langchain_openai as lang_oai

import re

# Load environment variables
load_dotenv()

gpt_4o_high_tokens = lang_oai.ChatOpenAI(
    model_name="gpt-4o",
    temperature=0.0,
    max_tokens=1500
)

# ---------- Utility Function ----------
def preprocess_data(data_df):
    """Prepares the data for Backtrader."""
    if isinstance(data_df.columns, pd.MultiIndex):
        data_df.columns = [' '.join(col).strip() for col in data_df.columns.values]
        data_df.columns = [col.split(' ')[0] for col in data_df.columns]

    if 'Adj Close' in data_df.columns:
        data_df['Close'] = data_df['Adj Close']

    data_df = data_df.rename(columns=str.lower)
    data_df = data_df[['open', 'high', 'low', 'close', 'volume']]
    data_df.dropna(inplace=True)

    return data_df

# ---------- Strategy Classes ----------
class DividendCrewAIStrategy(bt.Strategy):
    params = dict(company='AAPL', printlog=True)

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.forecasted_growth_rate = 0.0

    def fetch_dividend_forecast(self):
        """Fetches and parses the daily dividend growth forecast from CrewAI."""
        agents = StockAnalysisAgents(gpt_model=gpt_4o_high_tokens)
        tasks = StockAnalysisTasks()
        dividend_forecasting_agent = agents.dividend_forecasting_agent(self.params.company)

        financial_data = self.fetch_financial_data()
        dividend_forecasting_task = tasks.forecast_dividend_growth(
            dividend_forecasting_agent, financial_data, self.params.company
        )

        crew = Crew(
            agents=[dividend_forecasting_agent],
            tasks=[dividend_forecasting_task],
            verbose=False
        )
        crew_output = crew.kickoff()
        return self.parse_dividend_growth(crew_output)

    def fetch_financial_data(self):
        """Fetches financial data for the company."""
        ticker = Ticker(self.params.company)
        income_statement = ticker.income_statement(frequency='a')
        cash_flow_statement = ticker.cash_flow(frequency='a')
        return {
            "IncomeStatement": income_statement.to_string(),
            "CashFlowStatement": cash_flow_statement.to_string()
        }

    def parse_dividend_growth(self, crew_output):
        """Parses the dividend growth forecast from CrewAI output."""
        if hasattr(crew_output, 'tasks_output') and crew_output.tasks_output:
            task_output = crew_output.tasks_output[0]
            forecast_text = task_output.content if hasattr(task_output, 'content') else str(task_output)
        else:
            forecast_text = str(crew_output)

        matches = re.search(r'(\d+(\.\d+)?)%\s*increase', forecast_text)
        if matches:
            growth_rate = float(matches.group(1)) / 100  # Convert to decimal
            return growth_rate
        else:
            return 0.0

    def next(self):
        """Executes buy decision based on daily dividend forecast."""
        self.forecasted_growth_rate = self.fetch_dividend_forecast()
        self.log(f"Forecasted Growth Rate: {self.forecasted_growth_rate:.4f}")

        # Buy logic based on dividend growth forecast
        if self.forecasted_growth_rate > 0.00 and not self.position:
            size = self.broker.getcash() // self.data.close[0]
            self.order = self.buy(size=size)
            self.log(f"BUY CREATE, {self.dataclose[0]:.2f}")

    def log(self, txt, dt=None):
        """Logs important strategy events."""
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} {txt}")

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY EXECUTED, Price: {order.executed.price:.2f}")

class NonCrewAIStrategy(bt.Strategy):
    params = dict(allocation=1.0, printlog=True)

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

    def next(self):
        """Executes a simple buy-and-hold strategy."""
        if not self.position:
            size = self.broker.getcash() // self.data.close[0]
            self.order = self.buy(size=size)
            self.log(f"BUY CREATE, {self.dataclose[0]:.2f}")

    def log(self, txt, dt=None):
        """Logs important strategy events."""
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} {txt}")

# ---------- Backtest Runner ----------
def run_strategy(strategy_class, strategy_name, data_df, company=None):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    data_df = preprocess_data(data_df)
    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)

    if company:
        cerebro.addstrategy(strategy_class, company=company, printlog=True)
    else:
        cerebro.addstrategy(strategy_class, printlog=True)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.01)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, _name='timereturn')

    print(f"\nRunning {strategy_name}...")
    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
    results = cerebro.run()
    strat = results[0]
    final_value = cerebro.broker.getvalue()
    print(f"Final Portfolio Value: {final_value:.2f}")

    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    timereturn = strat.analyzers.timereturn.get_analysis()
    cumulative_return = (pd.Series(timereturn) + 1.0).prod() - 1.0 if timereturn else 0.0

    sharpe_ratio = sharpe.get('sharperatio', 'N/A') if sharpe else 'N/A'
    max_drawdown = drawdown.max.drawdown if drawdown else 0.0

    print(f"\n{strategy_name} Performance Metrics:")
    print(f"Sharpe Ratio: {sharpe_ratio}")
    print(f"Total Return: {cumulative_return * 100:.2f}%")
    print(f"Max Drawdown: {max_drawdown:.2f}%")

    return {
        "strategy_name": strategy_name,
        "sharpe_ratio": sharpe_ratio,
        "total_return": cumulative_return * 100,
        "max_drawdown": max_drawdown,
    }

# ---------- Main Logic ----------
if __name__ == "__main__":
    company = "AAPL"
    data_df = yf.download(company, start="2024-10-25", end="2024-10-30")

    if data_df.empty:
        print(f"No data found for {company}. Exiting.")
        exit()

    crewai_metrics = run_strategy(DividendCrewAIStrategy, "CrewAI Dividend Strategy", data_df, company)
    noncrewai_metrics = run_strategy(NonCrewAIStrategy, "Buy-and-Hold Strategy", data_df)

    print("\nComparison of Strategies:")
    comparison = pd.DataFrame([crewai_metrics, noncrewai_metrics])
    print(comparison)
