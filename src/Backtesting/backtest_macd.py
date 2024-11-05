import backtrader as bt
import pandas as pd
from src.Agents.MACD.macd_analysis_agent import MACDAnalysisAgent
from src.Indicators.macd import MACDIndicator
import yfinance as yf 
from crewai import Crew

import backtrader as bt
from crewai import Crew
from src.Agents.MACD.macd_analysis_agent import MACDAnalysisAgent
from src.Indicators.macd import MACDIndicator

import backtrader as bt
from crewai import Crew
from src.Agents.MACD.macd_analysis_agent import MACDAnalysisAgent
from src.Indicators.macd import MACDIndicator

import backtrader as bt
from crewai import Crew, Agent
from langchain_openai import ChatOpenAI
from src.Indicators.macd import MACDIndicator
from src.Agents.Analysis.Tools.browser_tools import BrowserTools
from src.Agents.Analysis.Tools.calculator_tools import CalculatorTools
from src.Agents.Analysis.Tools.search_tools import SearchTools
from src.Agents.Analysis.Tools.sec_tools import SECTools
from langchain_community.tools import YahooFinanceNewsTool

import backtrader as bt
from crewai import Crew, Agent, Task
from langchain_openai import ChatOpenAI
from src.Indicators.macd import MACDIndicator
from src.Agents.Analysis.Tools.browser_tools import BrowserTools
from src.Agents.Analysis.Tools.calculator_tools import CalculatorTools
from src.Agents.Analysis.Tools.search_tools import SearchTools
from src.Agents.Analysis.Tools.sec_tools import SECTools
from langchain_community.tools import YahooFinanceNewsTool

class MACDCrewAIStrategy(bt.Strategy):
    params = dict(
        company='AAPL',
        printlog=False,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

        # Initialize a direct Agent with the required parameters
        gpt_model = ChatOpenAI(
            temperature=0,
            model_name="gpt-4o"
        )
        
        macd_agent = Agent(
            llm=gpt_model,
            role='MACD Trading Advisor',
            goal="""Interpret MACD signals and provide actionable insights on market trends. 
                    Help traders identify potential bullish or bearish movements and offer advice 
                    on whether to buy, sell, or hold a stock.""",
            backstory="""As an expert in technical analysis, this agent specializes in MACD interpretation. 
                         It uses its deep knowledge of stock market trends to assist traders in making 
                         informed decisions based on MACD signals.""",
            verbose=True,
            tools=[
                BrowserTools.scrape_and_summarize_website,
                SearchTools.search_internet,
                CalculatorTools.calculate,
                SECTools.search_10q,
                SECTools.search_10k,
                YahooFinanceNewsTool()
            ]
        )

        # Calculate MACD data
        macd_data = MACDIndicator().calculate(self.data._dataname)
        
        # Define the description for the MACD analysis task
        description = f"""
            Analyze the provided MACD data, which includes the MACD Line, Signal Line, 
            and MACD Histogram. Based on these indicators, assess whether the stock 
            is showing bullish, bearish, or neutral signals. Additionally, provide 
            trading recommendations based on the MACD crossover or divergence.
            MACD Data:
            - MACD Line: {macd_data['MACD Line'].iloc[-1]}
            - Signal Line: {macd_data['Signal Line'].iloc[-1]}
            - MACD Histogram: {macd_data['MACD Histogram'].iloc[-1]}
        """

        # Create the task directly
        macd_task = Task(
            description=description,
            agent=macd_agent,
            expected_output="A report analyzing MACD signals with trading recommendations."
        )

        # Setup Crew to run the agent and task
        crew = Crew(
            agents=[macd_agent],
            tasks=[macd_task],
            verbose=True
        )
        
        # Kickoff CrewAI for analysis and retrieve output
        crew_output = crew.kickoff()
        
        # Parse the trading recommendation from Crew AI output
        self.recommendation = self.parse_crew_output(crew_output)

    def parse_crew_output(self, output):
        # Parse recommendation from Crew AI output if available
        if hasattr(output, 'tasks_output') and output.tasks_output:
            task_output = output.tasks_output[0]
            if hasattr(task_output, 'content'):
                return task_output.content.lower()
        return "hold"  # Default to "hold" if no recommendation

    def next(self):
        # Execute trades based on Crew AI recommendation
        if self.recommendation == "buy" and not self.position:
            self.order = self.buy()
            if self.params.printlog:
                self.log(f"BUY EXECUTED: {self.dataclose[0]:.2f}")
        elif self.recommendation == "sell" and self.position:
            self.order = self.sell()
            if self.params.printlog:
                self.log(f"SELL EXECUTED: {self.dataclose[0]:.2f}")





class StandardMACDStrategy(bt.Strategy):
    params = dict(
        short_period=12,
        long_period=26,
        signal_period=9,
        printlog=False,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        
        # Calculate MACD indicators
        macd_data = MACDIndicator(
            period_short=self.params.short_period,
            period_long=self.params.long_period,
            signal_period=self.params.signal_period
        ).calculate(self.data._dataname)
        
        self.macd_line = macd_data['MACD Line']
        self.signal_line = macd_data['Signal Line']

    def next(self):
        # Basic MACD crossover strategy
        if self.macd_line[0] > self.signal_line[0] and not self.position:
            self.order = self.buy()
            if self.params.printlog:
                self.log(f"BUY CREATE {self.dataclose[0]:.2f}")
        elif self.macd_line[0] < self.signal_line[0] and self.position:
            self.order = self.sell()
            if self.params.printlog:
                self.log(f"SELL CREATE {self.dataclose[0]:.2f}")

# Define the backtest function
def run_macd_backtest(strategy_class, strategy_name, data_df, company=None):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)
    
    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)
    
    if company:
        cerebro.addstrategy(strategy_class, company=company, printlog=True)
    else:
        cerebro.addstrategy(strategy_class, printlog=True)
    
    # Add analyzers for additional metrics
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, _name='timereturn')
    
    # Run the backtest
    results = cerebro.run()
    strat = results[0]
    
    # Retrieve and calculate performance metrics
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    timereturn = strat.analyzers.timereturn.get_analysis()
    
    # Calculate cumulative and annualized returns
    strategy_returns = pd.Series(timereturn)
    cumulative_return = (strategy_returns + 1.0).prod() - 1.0
    
    start_date = data_df.index[0]
    end_date = data_df.index[-1]
    num_years = (end_date - start_date).days / 365.25
    
    annual_return = (1 + cumulative_return) ** (1 / num_years) - 1 if num_years > 0 else 0.0
    
    # Plot the results
    cerebro.plot(style='candlestick')
    
    # Print and return the performance metrics
    metrics = {
        'strategy_name': strategy_name,
        'sharpe_ratio': sharpe.get('sharperatio', 'N/A'),
        'total_return': cumulative_return * 100,
        'annual_return': annual_return * 100,
        'max_drawdown': drawdown.max.drawdown,
    }
    print(metrics)
    return metrics

# Run both strategies
data_df = yf.download("AAPL", start="2020-01-01", end="2024-10-30")
macd_crew_metrics = run_macd_backtest(MACDCrewAIStrategy, "MACD CrewAI", data_df, company="AAPL")
macd_standard_metrics = run_macd_backtest(StandardMACDStrategy, "MACD Standard", data_df)

# Display the results
print("MACD CrewAI Metrics:", macd_crew_metrics)
print("MACD Standard Metrics:", macd_standard_metrics)
