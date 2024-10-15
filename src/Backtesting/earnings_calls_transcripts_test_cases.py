import unittest
from unittest.mock import patch, Mock
from src.UI.earnings_calls_sec_filings_app import FinancialCrew
from src.Agents.Earnings_Calls_Sec_Filings_Agents.earnings_sec_analysis_agents import EarningsSecAnalysisAgents


class TestEarningsSecAnalysis(unittest.TestCase):

    @patch('src.UI.earnings_calls_sec_filings_app.FinancialCrew.fetch_sec_filings')
    def test_sec_filings_analysis(self, mock_fetch_sec_filings):
        # Mock SEC filings data
        mock_sec_data = '{"sec_filings": [{"type": "10-K", "filingDate": "2022-12-31"}]}'
        mock_fetch_sec_filings.return_value = mock_sec_data

        agents = EarningsSecAnalysisAgents()
        agent = agents.financial_analyst()
        task = agents.analyze_sec_filings(agent, mock_sec_data)

        self.assertIn('A detailed analysis of SEC filings', task.expected_output)
        self.assertEqual(task.agent, agent)

    @patch('src.UI.earnings_calls_sec_filings_app.FinancialCrew.fetch_earnings_calls')
    def test_earnings_calls_analysis(self, mock_fetch_earnings_calls):
        # Mock earnings call data
        mock_earnings_data = '{"earnings_calls": [{"date": "2023-01-25", "quarter": "Q4"}]}'
        mock_fetch_earnings_calls.return_value = mock_earnings_data

        agents = EarningsSecAnalysisAgents()
        agent = agents.financial_analyst()
        task = agents.analyze_earnings_calls(agent, mock_earnings_data)

        self.assertIn('A detailed earnings call analysis', task.expected_output)
        self.assertEqual(task.agent, agent)

if __name__ == '__main__':
    unittest.main()
