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

    def test_market_scenarios(self):
        # Simulate different scenarios
        mock_sentiment_data = {"sentiment_score": 0.85}  # Positive sentiment
        buy_task = self.decision_agent.make_decision()
        self.assertIn('buy', buy_task.expected_output.lower())

        mock_sentiment_data = {"sentiment_score": 0.45}  # Negative sentiment
        sell_task = self.decision_agent.make_decision()
        self.assertIn('sell', sell_task.expected_output.lower())

        mock_sentiment_data = {"sentiment_score": 0.50}  # Neutral sentiment
        hold_task = self.decision_agent.make_decision()
        self.assertIn('hold', hold_task.expected_output.lower())

class TestTimingTradingSystem(unittest.TestCase):

    @patch('src.Data_Retrieval.timing_trading_data_fetcher.DataFetcher.get_earnings_date')
    @patch('src.Data_Retrieval.timing_trading_data_fetcher.DataFetcher.get_stock_news')
    def test_integration_sentiment_analysis_before_earnings(self, mock_get_stock_news, mock_get_earnings_date):
        # Mock stock news and earnings date
        mock_get_earnings_date.return_value = "2024-10-30"
        mock_get_stock_news.return_value = [{"summary": "Positive earnings report expected"}]

        # Test the full workflow for sentiment analysis
        trading_system = TimingTradingSystem("AAPL")
        result = trading_system.run()
        self.assertIn("Sentiment analysis report", result)

    @patch('src.Data_Retrieval.timing_trading_data_fetcher.DataFetcher.get_earnings_date')
    @patch('src.Data_Retrieval.timing_trading_data_fetcher.DataFetcher.get_stock_news')
    def test_cross_validation_with_multiple_timeframes(self, mock_get_stock_news, mock_get_earnings_date):
        # Simulate multiple timeframes and varying sentiment
        mock_get_earnings_date.return_value = "2024-10-30"
        mock_get_stock_news.side_effect = [
            [{"summary": "Positive sentiment in early Q3"}],
            [{"summary": "Negative sentiment in late Q3"}]
        ]

        trading_system = TimingTradingSystem("AAPL")
        result = trading_system.run()
        self.assertIn("Sentiment analysis report", result)

    @patch('src.Data_Retrieval.timing_trading_data_fetcher.DataFetcher.get_earnings_date')
    @patch('src.Data_Retrieval.timing_trading_data_fetcher.DataFetcher.get_stock_news')
    def test_timing_strategy_with_earnings_reports(self, mock_get_stock_news, mock_get_earnings_date):
        # Simulate timing strategy with earnings reports
        mock_get_earnings_date.return_value = "2024-11-15"
        mock_get_stock_news.return_value = [{"summary": "Mixed earnings forecast"}]

        trading_system = TimingTradingSystem("AAPL")
        result = trading_system.run()
        self.assertIn("buy/sell recommendation", result)


   
if __name__ == '__main__':
    unittest.main()
