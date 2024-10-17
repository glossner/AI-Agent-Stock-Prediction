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

    @patch('src.Agents.Analysis.stock_analysis_agents.StockAnalysisAgents.sentiment_analyst')
    @patch('src.Agents.Analysis.stock_analysis_agents.StockAnalysisAgents.research_analyst')
    def test_run(self, mock_research_analyst, mock_sentiment_analyst):
        mock_research_analyst.return_value = MagicMock()
        mock_sentiment_analyst.return_value = MagicMock()
        result = self.sentiment_crew.run()
        self.assertIn("Sentiment Analysis Report", result)

    @patch('src.Data_Retrieval.timing_trading_data_fetcher.DataFetcher.get_stock_news')
    def test_api_interaction_error(self, mock_get_stock_news):
        mock_get_stock_news.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.sentiment_crew.run()

class TestSentimentAnalysisIntegration(unittest.TestCase):

    @patch('src.Agents.Analysis.stock_analysis_tasks.StockAnalysisTasks.fetch_news')
    @patch('src.Agents.Analysis.stock_analysis_tasks.StockAnalysisTasks.analyze_sentiment')
    @patch('src.Agents.Analysis.stock_analysis_tasks.StockAnalysisTasks.provide_investment_advice')
    def test_integration_sentiment_analysis_and_advice(self, mock_provide_investment_advice, mock_analyze_sentiment, mock_fetch_news):
        mock_fetch_news.return_value = "Positive sentiment on AAPL"
        mock_analyze_sentiment.return_value = "Positive"
        mock_provide_investment_advice.return_value = "Buy recommendation"
        sentiment_crew = SentimentCrew("AAPL")
        result = sentiment_crew.run()
        self.assertIn("Buy recommendation", result)

    @patch('src.Agents.Analysis.stock_analysis_tasks.StockAnalysisTasks.fetch_news')
    @patch('src.Agents.Analysis.stock_analysis_tasks.StockAnalysisTasks.analyze_sentiment')
    def test_sentiment_analysis_with_multiple_data_sources(self, mock_analyze_sentiment, mock_fetch_news):
        mock_fetch_news.side_effect = ["News1", "News2"]
        mock_analyze_sentiment.return_value = "Mixed"
        sentiment_crew = SentimentCrew("Tech Sector")
        result = sentiment_crew.run()
        self.assertIn("Mixed", result)

    @patch('src.Agents.Analysis.stock_analysis_tasks.StockAnalysisTasks.fetch_news')
    @patch('src.Agents.Analysis.stock_analysis_tasks.StockAnalysisTasks.analyze_sentiment')
    def test_cross_source_sentiment_accuracy(self, mock_analyze_sentiment, mock_fetch_news):
        mock_fetch_news.return_value = "Mixed sentiments across sources"
        mock_analyze_sentiment.return_value = "Neutral"
        sentiment_crew = SentimentCrew("MSFT")
        result = sentiment_crew.run()
        self.assertIn("Neutral", result)

if __name__ == "__main__":
    unittest.main()
