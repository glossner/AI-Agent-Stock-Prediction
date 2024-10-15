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

if __name__ == '__main__':
    unittest.main()
