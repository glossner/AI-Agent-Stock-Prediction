import backtrader as bt
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
import os
from crewai import Crew
import sys

# Load environment variables
load_dotenv()

# Insert the project directory to sys.path to import custom modules
# Adjust the path as necessary based on your project structure
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import custom modules
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks
from src.Agents.divergence_agents.divergence_agent import DivergenceAnalysisAgents, DivergenceAnalysisTasks
from src.Data_Retrieval.data_fetcher import DataFetcher
from src.Indicators.rsi_divergence import RSIIndicator
from src.Indicators.macd_indicator import MACDIndicator
from detect_divergence import DivergenceDetector  # Ensure this path is correct

# ===========================
# Divergence Detector Class
# ===========================
# (Already provided in detect_divergence.py)
# Ensure that detect_divergence.py is correctly placed and accessible

# =====================================
# CrewAI-based Divergence Strategy
# =====================================
class DivergenceCrewAIStrategy(bt.Strategy):
    params = dict(
        company='AAPL',
        indicator='MACD',  # Options: 'MACD' or 'RSI'
        data_df=None,
        printlog=True,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.company = self.params.company
        self.indicator = self.params.indicator

        # Access the DataFrame passed via parameters
        data_df = self.params.data_df

        # Initialize Agents and Tasks
        divergence_agents = DivergenceAnalysisAgents()
        divergence_tasks = DivergenceAnalysisTasks()

        # Calculate Indicator Values
        if self.indicator == 'MACD':
            self.indicator_data = MACDIndicator().calculate(data_df)
        elif self.indicator == 'RSI':
            self.indicator_data = RSIIndicator().calculate(data_df)
        else:
            raise ValueError("Indicator must be 'MACD' or 'RSI'")

        # Initialize CrewAI Agent and Task
        self.divergence_agent = divergence_agents.divergence_trading_advisor()
        self.divergence_task = divergence_tasks.detect_divergence(
            self.divergence_agent, data_df, self.indicator_data, self.indicator
        )

        # Run CrewAI
        crew = Crew(
            agents=[self.divergence_agent],
            tasks=[self.divergence_task],
            verbose=True
        )
        self.crew_output = crew.kickoff()

        # Parse Divergence Signals
        self.bullish_dates, self.bearish_dates = self.parse_divergence_signals(self.crew_output)

        # Debug: Print Parsed Divergence Dates
        print(f"Parsed Bullish Divergence Dates: {self.bullish_dates}")
        print(f"Parsed Bearish Divergence Dates: {self.bearish_dates}")

    def parse_divergence_signals(self, crew_output):
        bullish_dates = []
        bearish_dates = []

        if hasattr(crew_output, 'tasks_output') and crew_output.tasks_output:
            task_output = crew_output.tasks_output[0]
            if hasattr(task_output, 'content'):
                bullish_dates = task_output.content.get('Bullish Divergences', [])
                bearish_dates = task_output.content.get('Bearish Divergences', [])

        return bullish_dates, bearish_dates

    def next(self):
        current_date = self.datas[0].datetime.date(0)
        close_price = self.dataclose[0]

        # Debug: Print Current Date and Close Price
        print(f"{current_date} Close Price: {close_price}")

        if pd.isna(close_price):
            self.log(f'Close price is NaN on {current_date}')
            return

        # Execute Buy Order on Bullish Divergence
        if str(current_date) in self.bullish_dates and not self.position:
            self.order = self.buy()
            if self.params.printlog:
                self.log(f'BUY CREATE, {close_price:.2f}')

        # Execute Sell Order on Bearish Divergence
        elif str(current_date) in self.bearish_dates and self.position:
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

# ====================================
# Non-CrewAI Divergence Strategy
# ====================================
class DivergenceStrategy(bt.Strategy):
    params = dict(
        data_df=None,
        indicator='MACD',  # Options: 'MACD' or 'RSI'
        printlog=True,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

        # Access the DataFrame passed via parameters
        data_df = self.params.data_df

        # Calculate Indicator Values
        if self.params.indicator == 'MACD':
            self.indicator_data = MACDIndicator().calculate(data_df)
        elif self.params.indicator == 'RSI':
            self.indicator_data = RSIIndicator().calculate(data_df)
        else:
            raise ValueError("Indicator must be 'MACD' or 'RSI'")

        # Initialize Divergence Detector
        detector = DivergenceDetector(data_df, self.indicator_data, self.params.indicator)
        self.bullish_dates = detector.detect_bullish_divergence()
        self.bearish_dates = detector.detect_bearish_divergence()

        # Debug: Print Detected Divergence Dates
        print(f"Detected Bullish Divergence Dates: {self.bullish_dates}")
        print(f"Detected Bearish Divergence Dates: {self.bearish_dates}")

    def next(self):
        current_date = self.datas[0].datetime.date(0)
        close_price = self.dataclose[0]

        # Debug: Print Current Date and Close Price
        print(f"{current_date} Close Price: {close_price}")

        if pd.isna(close_price):
            self.log(f'Close price is NaN on {current_date}')
            return

        # Execute Buy Order on Bullish Divergence
        if str(current_date) in self.bullish_dates and not self.position:
            self.order = self.buy()
            if self.params.printlog:
                self.log(f'BUY CREATE, {close_price:.2f}')

        # Execute Sell Order on Bearish Divergence
        elif str(current_date) in self.bearish_dates and self.position:
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

# ===============================
# Backtesting Runner Function
# ===============================
def run_strategy(strategy_class, strategy_name, data_df, company=None, indicator='MACD'):
    # Preprocess DataFrame
    try:
        # Print original columns
        print("\nOriginal DataFrame Columns:")
        print(data_df.columns)

        # 1. Flatten MultiIndex columns if present
        if isinstance(data_df.columns, pd.MultiIndex):
            data_df.columns = ['_'.join(col).strip() for col in data_df.columns.values]
            print("Flattened MultiIndex columns.")

        # 2. Standardize column names to title case and remove ticker suffix
        data_df.columns = [str(col).strip().title() for col in data_df.columns]
        print("Standardized column names to title case.")

        # 3. Remove ticker suffix (e.g., '_AAPL') from column names
        data_df.columns = [col.split('_')[0] if '_' in col else col for col in data_df.columns]
        print("Removed ticker suffix from column names.")

        # 4. If 'Adj Close' exists, use it as 'Close'
        if 'Adj Close' in data_df.columns:
            data_df['Close'] = data_df['Adj Close']
            print("Replaced 'Close' with 'Adj Close'.")
        elif 'Close' not in data_df.columns:
            raise ValueError("Missing 'Close' column.")
        else:
            print("'Close' column is present.")

        # 5. Retain only required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_columns if col not in data_df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns in data_df: {missing_cols}")
        data_df = data_df[required_columns]
        print(f"Retained required columns: {required_columns}")

        # 6. Reset index to make 'Date' a column
        if 'Date' in data_df.index.names:
            data_df = data_df.reset_index()
            print("Reset index to make 'Date' a column.")

        # 7. Rename 'Date' to 'datetime'
        if 'Date' in data_df.columns:
            data_df.rename(columns={'Date': 'datetime'}, inplace=True)
            print("Renamed 'Date' to 'datetime'.")
        elif 'Datetime' in data_df.columns:
            data_df.rename(columns={'Datetime': 'datetime'}, inplace=True)
            print("Renamed 'Datetime' to 'datetime'.")
        else:
            raise ValueError("Date column not found in data_df. It should be 'Date' or 'Datetime'.")

        # 8. Convert 'datetime' to datetime objects
        data_df['datetime'] = pd.to_datetime(data_df['datetime'])
        print("Converted 'datetime' column to datetime objects.")

        # 9. Drop rows with NaN in 'Close'
        if data_df['Close'].isna().any():
            print("Warning: 'Close' column contains NaN values. Dropping these rows.")
            data_df = data_df.dropna(subset=['Close'])

        # 10. Debug: Check DataFrame Structure
        print("\nDataFrame Columns and Types:")
        print(data_df.dtypes)
        print("\nFirst 5 Rows of DataFrame:")
        print(data_df.head())

    except Exception as e:
        print(f"Error during data preprocessing: {e}")
        return

    # Initialize Cerebro Engine
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)  # Starting with $100,000
    cerebro.broker.setcommission(commission=0.001)  # 0.1% commission

    # Create Data Feed for Backtrader
    try:
        data = bt.feeds.PandasData(
            dataname=data_df,
            datetime='datetime',
            open='Open',
            high='High',
            low='Low',
            close='Close',
            volume='Volume',
            openinterest=-1
        )
        cerebro.adddata(data)
        print("Added data feed to Cerebro.")
    except Exception as e:
        print(f"Error adding data feed to Cerebro: {e}")
        return

    # Add Strategy to Cerebro
    try:
        # Only pass 'company' if the strategy expects it
        if company and hasattr(strategy_class, 'params') and 'company' in strategy_class.params:
            cerebro.addstrategy(strategy_class, company=company, data_df=data_df, indicator=indicator, printlog=True)
        else:
            cerebro.addstrategy(strategy_class, data_df=data_df, indicator=indicator, printlog=True)
        print(f"Added strategy '{strategy_name}' to Cerebro.")
    except Exception as e:
        print(f"Error adding strategy to Cerebro: {e}")
        return

    # Add Analyzers
    try:
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, _name='timereturn')
        print("Added analyzers to Cerebro.")
    except Exception as e:
        print(f"Error adding analyzers to Cerebro: {e}")
        return

    # Run Backtest
    print(f'\nRunning {strategy_name}...')
    try:
        results = cerebro.run()
        print(f'Final Portfolio Value: {cerebro.broker.getvalue():.2f}')
    except Exception as e:
        print(f"Error during Cerebro run: {e}")
        return

    # Retrieve Analyzers
    try:
        strat = results[0]
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        timereturn = strat.analyzers.timereturn.get_analysis()
    except Exception as e:
        print(f"Error retrieving analyzers: {e}")
        return

    # Calculate Returns
    strategy_returns = pd.Series(timereturn)
    cumulative_return = (strategy_returns + 1.0).prod() - 1.0
    start_date = data_df['datetime'].iloc[0]
    end_date = data_df['datetime'].iloc[-1]
    num_years = (end_date - start_date).days / 365.25
    annual_return = (1 + cumulative_return) ** (1 / num_years) - 1 if num_years else 0.0

    # Print Performance Metrics
    print(f'\n{strategy_name} Performance Metrics:')
    print('----------------------------------------')
    print(f"Sharpe Ratio: {sharpe.get('sharperatio', 'N/A')}")
    print(f"Total Return: {cumulative_return * 100:.2f}%")
    print(f"Annual Return: {annual_return * 100:.2f}%")
    print(f"Max Drawdown: {drawdown.max.drawdown:.2f}%")

    # Optional: Plot the Strategy Results
    # cerebro.plot(style='candlestick')

    # Return Metrics
    return {
        'strategy_name': strategy_name,
        'sharpe_ratio': sharpe.get('sharperatio', 'N/A'),
        'total_return': cumulative_return * 100,
        'annual_return': annual_return * 100,
        'max_drawdown': drawdown.max.drawdown,
    }

# ===============================
# Main Backtesting Execution
# ===============================
if __name__ == '__main__':
    company = 'AAPL'
    data_df = yf.download(company, start='2020-01-01', end='2024-10-30')

    if data_df.empty:
        print(f"No price data found for {company}")
        sys.exit()

    # Run CrewAI-based Divergence Strategy
    try:
        metrics_crewai = run_strategy(
            DivergenceCrewAIStrategy,
            'Divergence CrewAI Strategy',
            data_df.copy(),
            company=company,
            indicator='MACD'  # Change to 'RSI' if needed
        )
    except Exception as e:
        print(f"Error running Divergence CrewAI Strategy: {e}")

    # Run Non-CrewAI Divergence Strategy
    try:
        metrics_noncrewai = run_strategy(
            DivergenceStrategy,
            'Divergence Non-CrewAI Strategy',
            data_df.copy(),
            indicator='MACD'  # Change to 'RSI' if needed
        )
    except Exception as e:
        print(f"Error running Divergence Non-CrewAI Strategy: {e}")

    # Compare the performance metrics
    print("\nComparison of Strategies:")
    print("-------------------------")
    metrics = ['strategy_name', 'sharpe_ratio', 'total_return', 'annual_return', 'max_drawdown']
    comparison_data = []
    if 'metrics_crewai' in locals() and metrics_crewai:
        comparison_data.append([
            metrics_crewai['strategy_name'],
            metrics_crewai['sharpe_ratio'],
            metrics_crewai['total_return'],
            metrics_crewai['annual_return'],
            metrics_crewai['max_drawdown']
        ])
    if 'metrics_noncrewai' in locals() and metrics_noncrewai:
        comparison_data.append([
            metrics_noncrewai['strategy_name'],
            metrics_noncrewai['sharpe_ratio'],
            metrics_noncrewai['total_return'],
            metrics_noncrewai['annual_return'],
            metrics_noncrewai['max_drawdown']
        ])
    if comparison_data:
        df_metrics = pd.DataFrame(comparison_data, columns=metrics)
        print(df_metrics.to_string(index=False))
    else:
        print("No metrics to compare.")