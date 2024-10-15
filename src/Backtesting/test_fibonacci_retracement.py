import unittest
from unittest.mock import patch
import pandas as pd
from src.Indicators.fibonacci import FibonacciRetracement
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.UI.main2 import FinancialCrew


# Unit Tests
class TestFibonacciRetracement(unittest.TestCase):

    def setUp(self):
        self.valid_data = pd.DataFrame({
            'High': [120, 130, 140],
            'Low': [100, 110, 115]
        })
        self.invalid_data = pd.DataFrame({
            'High': [120, 110],
            'Low': [130, 120]
        })
        self.fibonacci = FibonacciRetracement(self.valid_data)

    def test_invalid_high_low(self):
        fib = FibonacciRetracement(self.invalid_data)
        with self.assertRaises(ValueError):
            fib.calculate_levels()

    def test_identify_retracement_pattern(self):
        levels = self.fibonacci.calculate_levels()
        self.assertIn('61.8%', levels)


if __name__ == '__main__':
    unittest.main()
