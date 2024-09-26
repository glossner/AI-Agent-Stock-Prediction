from crewai import Task
from textwrap import dedent

class StockAnalysisTasks:
    def calculate_correlation(self, agent, stock1, stock2):
        return Task(
            description=dedent(f"""
                Analyze the historical price data of {stock1} and {stock2} to calculate their correlation.
                Based on the correlation results, determine if the stocks are suitable for pairs trading.
            """),
            agent=agent,
            expected_output="A report on the correlation between the two stocks and its significance for investment."
        )

    def investment_decision(self, agent, stock1, stock2):
        return Task(
            description=dedent(f"""
                Based on the correlation analysis between {stock1} and {stock2}, provide an investment decision.
                Consider market trends, risk factors, and the potential for profit in pairs trading with these stocks.
            """),
            agent=agent,
            expected_output="A detailed investment decision report, including buy/sell recommendations."
        )
