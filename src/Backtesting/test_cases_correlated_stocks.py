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

    def test_crew_initialization(self):
        """Unit test for initializing CrewAI."""
        crew = StockCorrelationCrew(stock1="AAPL", stock2="MSFT")
        self.assertEqual(crew.stock1, "AAPL")
        self.assertEqual(crew.stock2, "MSFT")

    def test_fetch_stock_data(self):
        """Unit test for fetching stock data."""
        with patch('src.Data_Retrieval.data_fetcher.DataFetcher.get_stock_data') as mock_fetch:
            mock_fetch.return_value = mock_stock_data
            agent = CorrelationAgent(stock1="AAPL", stock2="MSFT")
            result = agent.calculate_correlation()
            self.assertIn("The correlation between", result.description)

if __name__ == '__main__':
    unittest.main()
