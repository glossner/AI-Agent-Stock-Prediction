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

    def test_invalid_stock_tickers(self):
        """Unit test for handling invalid stock tickers."""
        with patch('src.Data_Retrieval.data_fetcher.DataFetcher.get_stock_data') as mock_fetch:
            mock_fetch.return_value = mock_invalid_stock_data
            agent = CorrelationAgent(stock1="INVALID1", stock2="INVALID2")
            result = agent.calculate_correlation()
            self.assertEqual(result.expected_output, "The correlation between INVALID1 and INVALID2 is: nan")

    def test_correlation_with_insufficient_data(self):
        """Unit test for correlation with insufficient data."""
        with patch('src.Data_Retrieval.data_fetcher.DataFetcher.get_stock_data') as mock_fetch:
            mock_fetch.return_value = mock_insufficient_data
            agent = CorrelationAgent(stock1="AAPL", stock2="MSFT")
            result = agent.calculate_correlation()
            self.assertEqual(result.expected_output, "The correlation between AAPL and MSFT is: nan")

    def test_analyze_correlation(self):
        """Unit test for analyzing correlation using the agent."""
        agent = CorrelationAgent(stock1="AAPL", stock2="MSFT")
        result = agent.calculate_correlation()
        self.assertIn("Analyze the historical price data", result.description)

    def test_identify_trading_opportunities(self):
        """Unit test to identify trading opportunities from correlation."""
        agent = InvestmentDecisionAgent(stock1="AAPL", stock2="MSFT")
        result = agent.investment_decision()
        self.assertIn("provide an investment decision", result.description)

    def test_trading_signal_generation(self):
        """Unit test to test trading signal generation based on correlation."""
        agent = InvestmentDecisionAgent(stock1="AAPL", stock2="MSFT")
        result = agent.investment_decision()
        self.assertIn("buy/sell recommendations", result.expected_output)

class TestIntegrationCorrelation(unittest.TestCase):

    @patch('src.Data_Retrieval.data_fetcher.DataFetcher.get_stock_data')
    def test_integration_with_real_time_data_streams(self, mock_fetch):
        """Integration test with mock real-time data."""
        mock_fetch.side_effect = [mock_stock_data, mock_stock_data]
        crew = StockCorrelationCrew(stock1="AAPL", stock2="MSFT")
        result = crew.run()
        self.assertIn("correlation between AAPL and MSFT", result)

    @patch('src.Data_Retrieval.data_fetcher.DataFetcher.get_stock_data')
    def test_cross_correlation_accuracy(self, mock_fetch):
        """Integration test to check cross-correlation accuracy."""
        mock_fetch.side_effect = [mock_stock_data, mock_stock_data]
        crew = StockCorrelationCrew(stock1="AAPL", stock2="MSFT")
        result = crew.run()
        self.assertIn("correlation between AAPL and MSFT", result)

    @patch('src.Data_Retrieval.data_fetcher.DataFetcher.get_stock_data')
    def test_integration_with_diverse_stock_pairs(self, mock_fetch):
        """Integration test with different stock pairs."""
        mock_fetch.side_effect = [mock_stock_data, mock_stock_data]
        crew = StockCorrelationCrew(stock1="GOOG", stock2="TSLA")
        result = crew.run()
        self.assertIn("correlation between GOOG and TSLA", result)
        
if __name__ == '__main__':
    unittest.main()
