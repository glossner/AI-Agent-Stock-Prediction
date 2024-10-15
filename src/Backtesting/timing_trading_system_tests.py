import unittest
from unittest.mock import patch, MagicMock
from src.Agents.Timing_Trading_Agents.sentiment_analysis_agent import SentimentAnalysisAgent
from src.Agents.Timing_Trading_Agents.buy_sell_decision_agent import BuySellDecisionAgent
from src.UI.timing_trading_system import TimingTradingSystem
from src.Data_Retrieval.timing_trading_data_fetcher import DataFetcher


class TestSentimentAnalysisAgent(unittest.TestCase):

    def setUp(self):
        self.stock = "AAPL"
        self.earnings_dates = "2024-10-30"
        self.sentiment_agent = SentimentAnalysisAgent(self.stock, self.earnings_dates)

    def test_sentiment_score(self):
        # Mock data
        mock_news_data = [{"summary": "Apple's earnings outlook is positive."}]
        with patch('src.Data_Retrieval.timing_trading_data_fetcher.DataFetcher.get_stock_news', return_value=mock_news_data):
            sentiment_task = self.sentiment_agent.analyze_sentiment()
            self.assertIn('sentiment analysis', sentiment_task.description.lower())
            self.assertIn('sentiment score', sentiment_task.expected_output)

    def test_neutral_sentiment(self):
        # Test for neutral sentiment
        mock_news_data = [{"summary": "Apple's earnings outlook is neutral."}]
        with patch('src.Data_Retrieval.timing_trading_data_fetcher.DataFetcher.get_stock_news', return_value=mock_news_data):
            sentiment_task = self.sentiment_agent.analyze_sentiment()
            self.assertIn('neutral', sentiment_task.description.lower())

class TestBuySellDecisionAgent(unittest.TestCase):

    def setUp(self):
        self.stock = "AAPL"
        self.decision_agent = BuySellDecisionAgent(self.stock)

    def test_buy_sell_decision(self):
        # Mock sentiment data
        mock_sentiment_data = {"sentiment_score": 0.85}
        decision_task = self.decision_agent.make_decision()
        self.assertIn('buy/sell recommendation', decision_task.expected_output)
        
if __name__ == '__main__':
    unittest.main()
