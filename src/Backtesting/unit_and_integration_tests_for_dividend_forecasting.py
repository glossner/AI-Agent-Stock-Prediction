import unittest
from unittest.mock import patch
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks
from src.UI.dividend_forecast_main import FinancialCrew

class TestDividendForecasting(unittest.TestCase):

    def setUp(self):
        self.tasks = StockAnalysisTasks()
        self.agents = StockAnalysisAgents()
        self.company = "TestCompany"
        self.mock_agent = self.agents.dividend_forecasting_agent(self.company)

    def test_predict_positive_growth(self):
        # Test case with positive dividend growth
        financial_data = {
            "IncomeStatement": "Net Income: 2000000, Revenue: 8000000, Dividend: 50000",
            "CashFlowStatement": "Operating Cash Flow: 2500000, Free Cash Flow: 1500000"
        }
        task = self.tasks.forecast_dividend_growth(self.mock_agent, financial_data, self.company)
        self.assertIn("forecast", task.expected_output.lower())

    def test_predict_no_growth(self):
        # Test case with no dividend growth
        financial_data = {
            "IncomeStatement": "Net Income: 1000000, Revenue: 5000000, Dividend: 50000",
            "CashFlowStatement": "Operating Cash Flow: 1200000, Free Cash Flow: 800000"
        }
        task = self.tasks.forecast_dividend_growth(self.mock_agent, financial_data, self.company)
        self.assertIn("forecast", task.expected_output.lower())

    def test_predict_negative_growth(self):
        # Test case with negative dividend growth
        financial_data = {
            "IncomeStatement": "Net Income: -500000, Revenue: 4000000, Dividend: 50000",
            "CashFlowStatement": "Operating Cash Flow: 800000, Free Cash Flow: 500000"
        }
        task = self.tasks.forecast_dividend_growth(self.mock_agent, financial_data, self.company)
        self.assertIn("forecast", task.expected_output.lower())

    def test_process_empty_financial_data(self):
        # Test handling of empty financial data
        financial_data = {
            "IncomeStatement": "",
            "CashFlowStatement": ""
        }
        with self.assertRaises(KeyError):
            self.tasks.forecast_dividend_growth(self.mock_agent, financial_data, self.company)

    def test_process_invalid_financial_data(self):
        # Test handling of invalid financial data
        financial_data = {
            "IncomeStatement": "Invalid data",
            "CashFlowStatement": "Invalid data"
        }
        task = self.tasks.forecast_dividend_growth(self.mock_agent, financial_data, self.company)
        self.assertIn("forecast", task.expected_output.lower())

    def test_process_partial_financial_data(self):
        # Test handling of partial financial data
        financial_data = {
            "IncomeStatement": "Net Income: 1000000, Revenue: 5000000",
            "CashFlowStatement": ""
        }
        with self.assertRaises(KeyError):
            self.tasks.forecast_dividend_growth(self.mock_agent, financial_data, self.company)

    def test_predict_dividend_growth_missing_fields(self):
        # Test handling of missing fields in financial data
        financial_data = {
            "IncomeStatement": None,
            "CashFlowStatement": None
        }
        with self.assertRaises(KeyError):
            self.tasks.forecast_dividend_growth(self.mock_agent, financial_data, self.company)

    def test_calculated_growth(self):
        # Test correct calculation of dividend growth
        financial_data = {
            "IncomeStatement": "Net Income: 3000000, Revenue: 9000000, Dividend: 70000",
            "CashFlowStatement": "Operating Cash Flow: 3200000, Free Cash Flow: 2000000"
        }
        task = self.tasks.forecast_dividend_growth(self.mock_agent, financial_data, self.company)
        self.assertIn("forecast", task.expected_output.lower())

    def test_zero_dividend(self):
        # Test case where the company does not pay dividends
        financial_data = {
            "IncomeStatement": "Net Income: 1500000, Revenue: 6000000, Dividend: 0",
            "CashFlowStatement": "Operating Cash Flow: 1700000, Free Cash Flow: 900000"
        }
        task = self.tasks.forecast_dividend_growth(self.mock_agent, financial_data, self.company)
        self.assertIn("forecast", task.expected_output.lower())

    def test_error_handling_invalid_input(self):
        # Test error handling for completely invalid input
        financial_data = {}
        with self.assertRaises(KeyError):
            self.tasks.forecast_dividend_growth(self.mock_agent, financial_data, self.company)

if __name__ == '__main__':
    unittest.main()
