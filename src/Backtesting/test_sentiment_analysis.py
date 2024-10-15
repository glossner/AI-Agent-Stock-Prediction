import unittest
from unittest.mock import patch, MagicMock
from src.UI.sentiment_analysis import SentimentCrew
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents

class TestSentimentAnalysis(unittest.TestCase):

    def setUp(self):
        self.stock_or_sector = "AAPL"
        self.sentiment_crew = SentimentCrew(self.stock_or_sector)

    @patch('src.Agents.Analysis.stock_analysis_tasks.StockAnalysisTasks.fetch_news')
    def test_empty_stock_or_sector(self, mock_fetch_news):
        self.sentiment_crew.stock_or_sector = ""
        mock_fetch_news.return_value = ""
        result = self.sentiment_crew.run()
        self.assertIn("No news data", result)

    @patch('src.Agents.Analysis.stock_analysis_tasks.StockAnalysisTasks.fetch_news')
    def test_invalid_stock_or_sector(self, mock_fetch_news):
        self.sentiment_crew.stock_or_sector = "INVALID"
        mock_fetch_news.return_value = ""
        result = self.sentiment_crew.run()
        self.assertIn("No data found", result)
        
    @patch('src.Agents.Analysis.stock_analysis_tasks.StockAnalysisTasks.fetch_news')
    def test_fetch_news_called(self, mock_fetch_news):
        self.sentiment_crew.run()
        mock_fetch_news.assert_called_with(self.stock_or_sector)

    @patch('src.Agents.Analysis.stock_analysis_tasks.StockAnalysisTasks.analyze_sentiment')
    def test_empty_news_data(self, mock_analyze_sentiment):
        mock_analyze_sentiment.return_value = "No sentiment data available"
        result = self.sentiment_crew.run()
        self.assertIn("No sentiment data available", result)

    @patch('src.Agents.Analysis.stock_analysis_tasks.StockAnalysisTasks.provide_investment_advice')
    def test_provide_investment_advice(self, mock_investment_advice):
        mock_investment_advice.return_value = "Hold recommendation"
        result = self.sentiment_crew.run()
        self.assertIn("Hold recommendation", result)

if __name__ == "__main__":
    unittest.main()
