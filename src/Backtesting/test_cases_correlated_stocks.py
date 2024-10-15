import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.Indicators.correlation import CorrelationIndicator
from src.Agents.Correlation_Agents.correlation_agent import CorrelationAgent
from src.Agents.Correlation_Agents.investment_decision_agent import InvestmentDecisionAgent
from src.UI.correlated_stocks import StockCorrelationCrew

# Mock stock data
mock_stock_data = pd.DataFrame({
    'Close': [100, 101, 102, 103, 104]
})

mock_insufficient_data = pd.DataFrame({
    'Close': [100]
})

mock_invalid_stock_data = pd.DataFrame({
    'Close': []
})


class TestCorrelationIndicator(unittest.TestCase):

    def test_calculate_correlation(self):
        """Unit test for calculating correlation between two stocks."""
        correlation_indicator = CorrelationIndicator(mock_stock_data, mock_stock_data)
        result = correlation_indicator.calculate(mock_stock_data)
        self.assertEqual(result, 1.0)

    def test_correlation_agent_initialization(self):
        """Unit test for initializing the correlation agent."""
        agent = CorrelationAgent(stock1="AAPL", stock2="MSFT")
        self.assertEqual(agent.stock1, "AAPL")
        self.assertEqual(agent.stock2, "MSFT")

if __name__ == '__main__':
    unittest.main()
