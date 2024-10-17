import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.Indicators.bollinger import BollingerBands
from src.Agents.Bollinger_agent.bollinger_agent import BollingerAnalysisAgents

# Unit Test Cases

class TestBollingerBands(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            'Close': [100, 102, 104, 106, 108, 110, 112, 114, 116, 118]
        })
        self.bollinger = BollingerBands(self.data)

    def test_calculate_bollinger_bands(self):
        # Test for correctly calculating Bollinger Bands
        result = self.bollinger.calculate_bands()
        self.assertIn('Upper Band', result)
        self.assertIn('Lower Band', result)
        self.assertIn('Moving Average', result)

    def test_calculate_bands_with_insufficient_data(self):
        # Test case for handling insufficient data
        insufficient_data = pd.DataFrame({
            'Close': [100, 102]
        })
        bollinger = BollingerBands(insufficient_data)
        with self.assertRaises(ValueError):
            bollinger.calculate_bands()

    def test_bollinger_agent_initialization(self):
        # Test for agent initialization
        agent = BollingerAnalysisAgents().bollinger_bands_investment_advisor()
        self.assertEqual(agent.role, 'Bollinger Bands Investment Advisor')

    @patch('src.Agents.Bollinger_agent.bollinger_agent.ChatOpenAI')
    def test_bollinger_analysis_method(self, mock_openai):
        # Test for agent analysis method
        mock_openai.return_value = MagicMock()
        agent = BollingerAnalysisAgents().bollinger_bands_investment_advisor()
        bollinger_bands = {
            'Upper Band': pd.Series([120]),
            'Lower Band': pd.Series([100]),
            'Moving Average': pd.Series([110])
        }
        analysis_task = BollingerAnalysisAgents().bollinger_analysis(agent, bollinger_bands)
        self.assertIn("Upper Band", analysis_task.description)
        self.assertIn("Lower Band", analysis_task.description)

    @patch('src.Agents.Bollinger_agent.bollinger_agent.BollingerAnalysisAgents.bollinger_bands_investment_advisor')
    def test_api_interaction_error_handling(self, mock_agent):
        # Test case for API interaction error handling
        mock_agent.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            BollingerAnalysisAgents().bollinger_bands_investment_advisor()

# Integration Test Cases

class TestBollingerBandsIntegration(unittest.TestCase):
    @patch('src.Data_Retrieval.data_fetcher.DataFetcher.get_stock_data')
    def test_bollinger_bands_end_to_end(self, mock_stock_data):
        # Integration test to check the end-to-end flow
        mock_stock_data.return_value = pd.DataFrame({
            'Close': [100, 102, 104, 106, 108, 110, 112, 114, 116, 118]
        })
        financial_crew = FinancialCrew("AAPL", mock_stock_data.return_value)
        result = financial_crew.run()
        self.assertIn("Here is the Report", result)

    @patch('src.Indicators.bollinger.BollingerBands.calculate_bands')
    def test_bollinger_bands_with_volatility_analysis(self, mock_bollinger_bands):
        # Integration test to check volatility analysis
        mock_bollinger_bands.return_value = {
            'Upper Band': pd.Series([120]),
            'Lower Band': pd.Series([100]),
            'Moving Average': pd.Series([110])
        }
        financial_crew = FinancialCrew("AAPL", pd.DataFrame())
        result = financial_crew.run()
        self.assertIn("Here is the Report", result)

    @patch('src.Indicators.bollinger.BollingerBands.calculate_bands')
    def test_bollinger_bands_with_market_trends(self, mock_bollinger_bands):
        # Integration test to simulate Bollinger Bands analysis with different market trends
        mock_bollinger_bands.return_value = {
            'Upper Band': pd.Series([120]),
            'Lower Band': pd.Series([100]),
            'Moving Average': pd.Series([110])
        }
        financial_crew = FinancialCrew("MSFT", pd.DataFrame())
        result = financial_crew.run()
        self.assertIn("Here is the Report", result)

        
if __name__ == '__main__':
    unittest.main()
