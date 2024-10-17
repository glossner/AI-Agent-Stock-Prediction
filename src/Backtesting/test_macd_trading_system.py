import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from src.Agents.MACD.macd_analysis_agent import MACDAnalysisAgent
from src.Indicators.macd import MACDIndicator
from src.Data_Retrieval.data_fetcher import DataFetcher
from crewai import Crew

# Unit tests
class TestMACDIndicator(unittest.TestCase):

    def setUp(self):
        self.data = pd.DataFrame({
            'Close': [100, 102, 101, 105, 107, 110, 108, 111, 113]
        })
        self.macd_indicator = MACDIndicator()

    def test_calculate_macd_value(self):
        macd_data = self.macd_indicator.calculate(self.data)
        self.assertIn('MACD Line', macd_data.columns)
        self.assertIn('Signal Line', macd_data.columns)
        self.assertIn('MACD Histogram', macd_data.columns)

    def test_macd_trading_advisor_initialization(self):
        macd_agent = MACDAnalysisAgent().macd_trading_advisor()
        self.assertEqual(macd_agent.role, 'MACD Trading Advisor')
        self.assertIn('Interpret MACD signals', macd_agent.goal)

    def test_macd_analysis_task(self):
        agent = MACDAnalysisAgent().macd_trading_advisor()
        macd_data = self.macd_indicator.calculate(self.data)
        task = MACDAnalysisAgent().macd_analysis(agent, macd_data)
        self.assertIn('Analyze the provided MACD data', task.description)

    @patch('src.Data_Retrieval.data_fetcher.DataFetcher.get_stock_data')
    def test_fetching_stock_data(self, mock_get_stock_data):
        mock_get_stock_data.return_value = pd.DataFrame({
            'Close': [100, 102, 101, 105, 107]
        })
        data_fetcher = DataFetcher()
        stock_data = data_fetcher.get_stock_data('AAPL')
        self.assertFalse(stock_data.empty)

    def test_crew_ai_agents_initialization(self):
        macd_agent = MACDAnalysisAgent().macd_trading_advisor()
        self.assertEqual(macd_agent.role, 'MACD Trading Advisor')

# Integration tests
class TestMACDIntegration(unittest.TestCase):

    @patch('src.Data_Retrieval.data_fetcher.DataFetcher.get_stock_data')
    def test_macd_analysis_integration(self, mock_get_stock_data):
        mock_get_stock_data.return_value = pd.DataFrame({
            'Close': [100, 102, 101, 105, 107]
        })

        financial_crew = FinancialCrew('AAPL')
        result = financial_crew.run()

        self.assertIn('MACD Trading Advisor', result)

    @patch('src.Data_Retrieval.data_fetcher.DataFetcher.get_stock_data')
    def test_macd_signal_accuracy(self, mock_get_stock_data):
        mock_get_stock_data.return_value = pd.DataFrame({
            'Close': [100, 102, 101, 105, 107, 110, 108, 111, 113]
        })
        financial_crew = FinancialCrew('AAPL')
        result = financial_crew.run()

        self.assertIn('bullish', result)  # Check if the result includes MACD signals

    @patch('src.Data_Retrieval.data_fetcher.DataFetcher.get_stock_data')
    def test_macd_integration_with_trailing_stop(self, mock_get_stock_data):
        mock_get_stock_data.return_value = pd.DataFrame({
            'Close': [100, 102, 101, 105, 107, 110, 108, 111, 113]
        })
        financial_crew = FinancialCrew('AAPL')
        result = financial_crew.run()

        self.assertIn('trailing stop', result)  # Check if trailing stop logic is applied in the MACD analysis

if __name__ == '__main__':
    unittest.main()
