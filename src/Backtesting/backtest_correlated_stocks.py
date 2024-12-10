from datetime import datetime
import logging
import backtrader as bt
import pandas as pd
import re
from src.Data_Retrieval.data_fetcher import DataFetcher
from src.Agents.Correlation_Agents.correlation_agent import CorrelationAgent
from src.Agents.Correlation_Agents.investment_decision_agent import InvestmentDecisionAgent
import crewai as crewai

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class CorrelatedStocksStrategy(bt.Strategy):
    params = (
        ('correlation_threshold', 0.8),  # Threshold for strong correlation
        ('allocation', 1.0),             # Cash allocation for trades
    )

    def __init__(self):
        # Initialize CrewAI agents
        self.correlation_agent = CorrelationAgent(stock1="AAPL", stock2="MSFT")
        self.investment_decision_agent = InvestmentDecisionAgent(stock1="AAPL", stock2="MSFT")

        # Check initial correlation
        self.correlation_met = self.check_initial_correlation()

    def check_initial_correlation(self):
        # Create and run correlation task
        task = self.correlation_agent.calculate_correlation()
        crew = crewai.Crew(agents=[self.correlation_agent], tasks=[task], process=crewai.Process.sequential)
        result = crew.kickoff()
        
        # Extract correlation value from the result
        correlation_result = result.tasks_output[0].raw
        logging.info(f"Correlation response from CrewAI: {correlation_result}")

        match = re.search(r"correlation between \w+ and \w+ is: ([\d.]+)", correlation_result)
        if match:
            correlation_value = float(match.group(1).strip().rstrip('.'))
            logging.info(f"Calculated correlation: {correlation_value}")
            return correlation_value >= self.params.correlation_threshold
        else:
            logging.error("Failed to extract correlation value from CrewAI response.")
            return False

    def next(self):
        current_date = self.datas[0].datetime.date(0)

        if not self.position:
            # Check for buy signal when no position is open
            if self.correlation_met:
                task = self.investment_decision_agent.investment_decision()
                crew = crewai.Crew(agents=[self.investment_decision_agent], tasks=[task], process=crewai.Process.sequential)
                decision_result = crew.kickoff().tasks_output[0].raw

                # Log the decision and parse for a buy signal
                logging.info(f"Investment decision from CrewAI: {decision_result}")
                if "buy" in decision_result.lower():
                    cash = self.broker.getcash()
                    price = self.data0.close[0]
                    size = (cash * self.params.allocation) // price
                    self.buy(size=size)
                    logging.info(f"{current_date}: BUY {size} shares at {price:.2f} based on CrewAI decision")

        elif self.position:
            # Check for sell signal when in a position
            task = self.investment_decision_agent.investment_decision()
            crew = crewai.Crew(agents=[self.investment_decision_agent], tasks=[task], process=crewai.Process.sequential)
            decision_result = crew.kickoff().tasks_output[0].raw

            logging.info(f"Investment decision from CrewAI: {decision_result}")
            if "sell" in decision_result.lower():
                size = self.position.size
                price = self.data0.close[0]
                self.sell(size=size)
                logging.info(f"{current_date}: SELL {size} shares at {price:.2f} based on CrewAI decision")



class BuyAndHold(bt.Strategy):
    params = (
        ('allocation', 1.0),  # Allocate 100% of the available cash
    )

    def __init__(self):
        pass  # No indicators needed for Buy and Hold

    def next(self):
        current_date = self.datas[0].datetime.date(0)
        if not self.position:  # If not in a position
            cash = self.broker.getcash()
            price = self.data.close[0]
            size = (cash * self.params.allocation) // price
            self.buy(size=size)
            logging.info(f"{current_date}: BUY {size} shares at {price:.2f}")


def run_backtest(strategy_class, data_feed1, data_feed2=None, cash=10000, commission=0.001):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy_class)
    cerebro.adddata(data_feed1)  # Add first stock data feed

    # Only add the second data feed if it's provided and not None
    if data_feed2 is not None:
        cerebro.adddata(data_feed2)  # Add second stock data feed for correlation strategy

    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission)

    # Add analyzers to the backtest
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.01)
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    # Run the backtest
    logging.info(f"Running {strategy_class.__name__} Strategy...")
    result = cerebro.run()

    # Extract the strategy and analyzer data
    strat = result[0]
    sharpe = strat.analyzers.sharpe.get_analysis()
    returns = strat.analyzers.returns.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    max_drawdown_duration = drawdown.get('maxdrawdownperiod', 'N/A')

    # Log analysis
    logging.info(f"Returns Analysis for {strategy_class.__name__}:")
    logging.info("\n%s", returns)

    # Check if sharpe['sharperatio'] exists and is valid before printing
    sharpe_ratio = sharpe.get('sharperatio', None)
    if sharpe_ratio is not None:
        print(f"  Sharpe Ratio: {sharpe_ratio:.2f}")
    else:
        print("  Sharpe Ratio: N/A")

    # Print other statistics, with checks for None or missing data
    print(f"  Total Return: {returns.get('rtot', 0)*100:.2f}%")
    print(f"  Avg Daily Return: {returns.get('ravg', 0)*100:.2f}%")
    annual_return = ((1 + returns.get('ravg', 0))**252 - 1) if 'ravg' in returns else 0
    print(f"  Avg Annual Return: {annual_return*100:.2f}%")
    print(f"  Max Drawdown: {drawdown.get('drawdown', 0)*100:.2f}%")
    print(f"  Max Drawdown Duration: {max_drawdown_duration}")

    cerebro.plot()




if __name__ == '__main__':
    cash = 10000
    commission = 0.001

    # Define stock symbols and date range
    symbol1 = 'AAPL'
    symbol2 = 'MSFT'
    start = datetime(2015, 1, 1)
    end = datetime(2023, 1, 1)

    # Fetch data for both stocks
    data1 = DataFetcher().get_stock_data(symbol=symbol1, start_date=start, end_date=end)
    data2 = DataFetcher().get_stock_data(symbol=symbol2, start_date=start, end_date=end)

    # Convert pandas DataFrame into Backtrader data feeds
    data_feed1 = bt.feeds.PandasData(dataname=data1, fromdate=start, todate=end)
    data_feed2 = bt.feeds.PandasData(dataname=data2, fromdate=start, todate=end)

    print("*********************************************")
    print("********** CORRELATED STOCKS STRATEGY *******")
    print("*********************************************")
    run_backtest(strategy_class=CorrelatedStocksStrategy, data_feed1=data_feed1, data_feed2=data_feed2, cash=cash, commission=commission)

    print("*********************************************")
    print("************* BUY AND HOLD ******************")
    print("*********************************************")
    # Corrected argument to data_feed1
    run_backtest(strategy_class=BuyAndHold, data_feed1=data_feed1, cash=cash, commission=commission)

