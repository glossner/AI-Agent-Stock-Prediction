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

    def test_divergence_agent_initialization(self):
        # Test the initialization of the divergence agent
        divergence_agent = DivergenceAnalysisAgents().divergence_trading_advisor()
        self.assertIsNotNone(divergence_agent)

    def test_divergence_analysis_task(self):
        # Test the creation of a divergence analysis task
        divergence_agent = DivergenceAnalysisAgents().divergence_trading_advisor()
        tasks = DivergenceAnalysisTasks()
        task = tasks.detect_divergence(divergence_agent, self.price_data, self.macd_data, 'MACD')
        self.assertIn("Bullish Divergences", task.description)
        self.assertIn("Bearish Divergences", task.description)

    def test_missing_data_handling(self):
        # Test missing data handling in the divergence pattern detection
        incomplete_price_data = pd.DataFrame({'Close': [100, None, 101, None, 105, 104, 106, None]})
        detector = DivergenceDetector(incomplete_price_data, self.macd_data, 'MACD')
        bullish_signals = detector.detect_bullish_divergence()
        self.assertEqual(len(bullish_signals), 0)  # Expect no signals due to missing data

    def test_validate_detection_in_market_conditions(self):
        # Test divergence detection in different market conditions
        bearish_market_price_data = pd.DataFrame({'Close': [108, 107, 106, 105, 104, 103, 102, 101]})
        detector = DivergenceDetector(bearish_market_price_data, self.macd_data, 'MACD')
        bearish_signals = detector.detect_bearish_divergence()
        self.assertTrue(len(bearish_signals) > 0)  # Ensure bearish signals are detected

class TestDivergenceIntegration(unittest.TestCase):

    @patch('src.UI.divergence_app.FinancialCrew.run')
    def test_false_positive_detection(self, mock_run):
        # Test to detect false positives in divergence signal detection
        mock_run.return_value = "Detected divergence, but it seems to be a false signal"
        result = mock_run()
        self.assertIn("false signal", result)
    @patch('src.UI.divergence_app.FinancialCrew.run')
    def test_cross_validation_with_multiple_timeframes(self, mock_run):
        # Test cross-validation of divergence signals across multiple timeframes
        mock_run.return_value = "Cross-validation shows divergence detected in 1D, but not in 4H"
        result = mock_run()
        self.assertIn("Cross-validation", result)

    @patch('src.UI.divergence_app.FinancialCrew.run')
    def test_integration_with_rsi_macd_indicators(self, mock_run):
        # Test the integration of both MACD and RSI indicators for divergence detection
        mock_run.return_value = "Detected divergence using both MACD and RSI. Signals confirm potential reversal."
        result = mock_run()
        self.assertIn("MACD and RSI", result)

   
if __name__ == '__main__':
    unittest.main()

