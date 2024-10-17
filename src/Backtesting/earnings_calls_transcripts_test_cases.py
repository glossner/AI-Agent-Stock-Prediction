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

    @patch('src.UI.earnings_calls_sec_filings_app.FinancialCrew.fetch_earnings_transcript')
    def test_fetch_earnings_calls_transcript(self, mock_fetch_transcript):
        # Mock fetching transcript
        mock_transcript_data = 'This is a mock transcript of the earnings call.'
        mock_fetch_transcript.return_value = mock_transcript_data

        financial_crew = FinancialCrew("AAPL", "NASDAQ")
        result = financial_crew.fetch_earnings_transcript(2023, 4)

        self.assertEqual(result, mock_transcript_data)

    def test_empty_sec_filings(self):
        # Test case where no SEC filings are found
        financial_crew = FinancialCrew("AAPL", "NASDAQ")
        result = financial_crew.fetch_sec_filings()
        self.assertIsNone(result)

    def test_financial_analyst_initialization(self):
        # Test initialization of the financial analyst agent
        agents = EarningsSecAnalysisAgents()
        agent = agents.financial_analyst()
        self.assertEqual(agent.role, 'Financial Analyst')

    @patch('src.UI.earnings_calls_sec_filings_app.FinancialCrew.fetch_earnings_transcript')
    def test_fetch_earnings_transcripts_invalid_params(self, mock_fetch_transcript):
        # Mock invalid earnings call transcript fetch
        mock_fetch_transcript.return_value = None

        financial_crew = FinancialCrew("AAPL", "NASDAQ")
        result = financial_crew.fetch_earnings_transcript(2023, 4)
        self.assertIsNone(result)

    def test_invalid_json_response(self):
        # Test invalid JSON response handling
        financial_crew = FinancialCrew("AAPL", "NASDAQ")
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.side_effect = ValueError("Invalid JSON")
            result = financial_crew.fetch_earnings_calls()
            self.assertIsNone(result)

    def test_missing_earnings_data(self):
        # Test case for missing earnings data
        financial_crew = FinancialCrew("AAPL", "NASDAQ")
        with patch('src.UI.earnings_calls_sec_filings_app.FinancialCrew.fetch_earnings_calls', return_value=None):
            result = financial_crew.fetch_earnings_calls()
            self.assertIsNone(result)

class TestIntegrationEarningsSecFilings(unittest.TestCase):

    @patch('src.UI.earnings_calls_sec_filings_app.FinancialCrew.fetch_sec_filings')
    @patch('src.UI.earnings_calls_sec_filings_app.FinancialCrew.fetch_earnings_calls')
    def test_sec_filings_and_earnings_integration(self, mock_fetch_earnings_calls, mock_fetch_sec_filings):
        # Mock both SEC filings and earnings calls
        mock_sec_data = '{"sec_filings": [{"type": "10-K", "filingDate": "2022-12-31"}]}'
        mock_earnings_data = '{"earnings_calls": [{"date": "2023-01-25", "quarter": "Q4"}]}'
        mock_fetch_sec_filings.return_value = mock_sec_data
        mock_fetch_earnings_calls.return_value = mock_earnings_data

        financial_crew = FinancialCrew("AAPL", "NASDAQ")
        result = financial_crew.run()

        self.assertIn("SEC Data", result)
        self.assertIn("Earnings Data", result)

    @patch('src.UI.earnings_calls_sec_filings_app.FinancialCrew.fetch_sec_filings')
    @patch('src.UI.earnings_calls_sec_filings_app.FinancialCrew.fetch_earnings_calls')
    def test_sentiment_analysis_integration(self, mock_fetch_earnings_calls, mock_fetch_sec_filings):
        # Mock SEC filings and earnings call data
        mock_sec_data = '{"sec_filings": [{"type": "10-K", "filingDate": "2022-12-31"}]}'
        mock_earnings_data = '{"earnings_calls": [{"date": "2023-01-25", "quarter": "Q4"}]}'
        mock_fetch_sec_filings.return_value = mock_sec_data
        mock_fetch_earnings_calls.return_value = mock_earnings_data

        financial_crew = FinancialCrew("AAPL", "NASDAQ")
        result = financial_crew.run()

        self.assertIn("SEC Data", result)
        self.assertIn("Earnings Data", result)
        self.assertIn("sentiment", result)  # Verifying sentiment analysis

    @patch('src.UI.earnings_calls_sec_filings_app.FinancialCrew.fetch_earnings_transcript')
    @patch('src.UI.earnings_calls_sec_filings_app.FinancialCrew.fetch_sec_filings')
    @patch('src.UI.earnings_calls_sec_filings_app.FinancialCrew.fetch_earnings_calls')
    def test_integration_with_transcripts(self, mock_fetch_earnings_calls, mock_fetch_sec_filings, mock_fetch_transcript):
        # Mock SEC filings, earnings calls, and transcript data
        mock_sec_data = '{"sec_filings": [{"type": "10-K", "filingDate": "2022-12-31"}]}'
        mock_earnings_data = '{"earnings_calls": [{"date": "2023-01-25", "quarter": "Q4"}]}'
        mock_transcript_data = 'This is a mock transcript of the earnings call.'
        mock_fetch_sec_filings.return_value = mock_sec_data
        mock_fetch_earnings_calls.return_value = mock_earnings_data
        mock_fetch_transcript.return_value = mock_transcript_data

        financial_crew = FinancialCrew("AAPL", "NASDAQ")
        result = financial_crew.run()

        self.assertIn("SEC Data", result)
        self.assertIn("Earnings Data", result)
        self.assertIn("mock transcript", result)  # Verifying transcript analysis

if __name__ == '__main__':
    unittest.main()
