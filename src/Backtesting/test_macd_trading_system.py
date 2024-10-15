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


if __name__ == '__main__':
    unittest.main()
