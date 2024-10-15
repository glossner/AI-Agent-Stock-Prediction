import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.Indicators.detect_divergence import DivergenceDetector
from src.Agents.divergence_agents.divergence_agent import DivergenceAnalysisAgents, DivergenceAnalysisTasks
from src.Indicators.macd_indicator import MACDIndicator
from src.Indicators.rsi_divergence import RSIIndicator

class TestDivergenceDetection(unittest.TestCase):

    def setUp(self):
        self.price_data = pd.DataFrame({
            'Close': [100, 102, 101, 103, 105, 104, 106, 108]
        })

        self.macd_data = pd.DataFrame({
            'MACD': [0.5, 0.6, 0.4, 0.7, 0.5, 0.8, 0.3, 0.9]
        })

        self.rsi_data = pd.DataFrame({
            'RSI': [30, 32, 28, 35, 40, 37, 45, 50]
        })

    def test_input_data_format(self):
        # Ensure input data has required columns
        self.assertIn('Close', self.price_data.columns)
        self.assertIn('MACD', self.macd_data.columns)
        self.assertIn('RSI', self.rsi_data.columns)

    def test_bullish_divergence_detection(self):
        # Test bullish divergence detection using MACD
        detector = DivergenceDetector(self.price_data, self.macd_data, 'MACD')
        bullish_signals = detector.detect_bullish_divergence()
        self.assertTrue(len(bullish_signals) > 0)  # Ensure that some bullish signals are detected

    def test_bearish_divergence_detection(self):
        # Test bearish divergence detection using MACD
        detector = DivergenceDetector(self.price_data, self.macd_data, 'MACD')
        bearish_signals = detector.detect_bearish_divergence()
        self.assertTrue(len(bearish_signals) > 0)  # Ensure that some bearish signals are detected


if __name__ == '__main__':
    unittest.main()

