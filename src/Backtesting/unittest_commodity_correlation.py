import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.Data_Retrieval.data_fetcher_commodity import DataFetcher
from src.Agents.Commodity_Correlation_Agents.commodity_correlation_agent import CommodityCorrelationAgent 
from src.Agents.Commodity_Correlation_Agents.investment_decision_agent import InvestmentDecisionAgent
from src.Indicators.commodity_correlation import CommodityCorrelationIndicator
from src.UI.commodity_correlation_analysis import CommodityCorrelationCrew



import unittest
from unittest.mock import patch



class TestDataFetcher(unittest.TestCase):
    def setUp(self):
        self.fetcher = DataFetcher()

    def test_get_stock_data(self):
        stock_data = self.fetcher.get_stock_data("AAPL")
        self.assertFalse(stock_data.empty, "Stock data should not be empty")
        self.assertIn("Close_AAPL", stock_data.columns, "Stock data should contain Close column")

    def test_get_commodity_data(self):
        commodity_data = self.fetcher.get_commodity_data("OIL")
        self.assertFalse(commodity_data.empty, "Commodity data should not be empty")
        self.assertIn("Close_OIL", commodity_data.columns, "Commodity data should contain Close column")

    def test_get_commodity_data_invalid(self):
        with self.assertRaises(ValueError):
            self.fetcher.get_commodity_data("INVALID_COMMODITY")


class TestCommodityCorrelationAgent(unittest.TestCase):
    @patch("src.Agents.Commodity_Correlation_Agents.commodity_correlation_agent.DataFetcher.get_stock_data")
    @patch("src.Agents.Commodity_Correlation_Agents.commodity_correlation_agent.DataFetcher.get_commodity_data")
    def test_calculate_correlation(self, mock_commodity_data, mock_stock_data):
        mock_stock_data.return_value = pd.DataFrame({"Close_AAPL": [100, 101, 102, 103, 104]})
        mock_commodity_data.return_value = pd.DataFrame({"Close_OIL": [50, 51, 52, 53, 54]})

        agent = CommodityCorrelationAgent(stock="AAPL", commodity="OIL")
        task = agent.calculate_correlation()
        self.assertIn("correlation", task.expected_output, "Expected output should include correlation")


class TestInvestmentDecisionAgent(unittest.TestCase):
    def test_investment_decision(self):
        agent = InvestmentDecisionAgent(stock="AAPL", commodity="OIL")
        task = agent.investment_decision()
        self.assertIn("recommendation", task.expected_output.lower(), "Expected output should include recommendation")


class TestCommodityCorrelationIndicator(unittest.TestCase):
    def test_calculate_perfect_correlation(self):
        stock_data = pd.DataFrame({"Close": [1, 2, 3, 4, 5]})
        commodity_data = pd.DataFrame({"Close": [10, 20, 30, 40, 50]})

        indicator = CommodityCorrelationIndicator(stock_data, commodity_data)
        correlation = indicator.calculate()
        self.assertEqual(correlation, 1.0, "Perfect positive correlation should be 1.0")

    def test_calculate_negative_correlation(self):
        stock_data = pd.DataFrame({"Close": [1, 2, 3, 4, 5]})
        commodity_data = pd.DataFrame({"Close": [50, 40, 30, 20, 10]})

        indicator = CommodityCorrelationIndicator(stock_data, commodity_data)
        correlation = indicator.calculate()
        self.assertEqual(correlation, -1.0, "Perfect negative correlation should be -1.0")


class TestCommodityCorrelationCrew(unittest.TestCase):
    @patch("src.Agents.Commodity_Correlation_Agents.commodity_correlation_agent.DataFetcher.get_stock_data")
    @patch("src.Agents.Commodity_Correlation_Agents.commodity_correlation_agent.DataFetcher.get_commodity_data")
    def test_commodity_correlation_crew(self, mock_commodity_data, mock_stock_data):
        mock_stock_data.return_value = pd.DataFrame({"Close_AAPL": [100, 101, 102, 103, 104]})
        mock_commodity_data.return_value = pd.DataFrame({"Close_OIL": [50, 51, 52, 53, 54]})

        crew = CommodityCorrelationCrew(stock="AAPL", commodity="OIL")
        result = crew.run()
        self.assertIn("correlation", result, "Result should include correlation analysis")
        self.assertIn("recommendation", result, "Result should include investment recommendations")


if __name__ == "__main__":
    unittest.main()
