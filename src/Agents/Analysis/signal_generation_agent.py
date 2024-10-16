from src.Agents.base_agent import BaseAgent
import pandas as pd
import numpy as np
from datetime import datetime
from src.Agents.Analysis.trend_detection_agent import TrendDetectionAgent
from src.Agents.Analysis.trend_prediction_agent import TrendPredictionAgent

class SignalGenerationAgent(BaseAgent):
    def __init__(self, risk_tolerance='medium'):
        super().__init__(
            role='Signal Generation Agent',
            goal='Generate clear and actionable buy/sell signals based on trend analysis',
            backstory='Expert in synthesizing market trends and predictions to generate trading signals'
        )
        self.trend_detection_agent = TrendDetectionAgent()
        self.trend_prediction_agent = TrendPredictionAgent()
        self.risk_tolerance = risk_tolerance
        self.stop_loss_percentages = {'low': 0.02, 'medium': 0.05, 'high': 0.10}
        self.take_profit_percentages = {'low': 0.03, 'medium': 0.08, 'high': 0.15}

    def generate_signal(self, data, symbol):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input data must be a pandas DataFrame")
        
        if 'Close' not in data.columns:
            raise ValueError("DataFrame must contain a 'Close' column")

        current_price = data['Close'].iloc[-1]
        current_timestamp = data.index[-1]

        try:
            # Get trend from TrendDetectionAgent
            detected_trend = self.trend_detection_agent.analyze_trend(data)

            # Get prediction from TrendPredictionAgent
            predicted_trend, _ = self.trend_prediction_agent.predict_trend(data, model_type='arima')

            # Define signal criteria
            if detected_trend == "Uptrend" and predicted_trend == "Uptrend":
                signal = "BUY"
            elif detected_trend == "Downtrend" and predicted_trend == "Downtrend":
                signal = "SELL"
            else:
                signal = "HOLD"

            # Calculate stop-loss and take-profit levels
            stop_loss = self.calculate_stop_loss(current_price, signal)
            take_profit = self.calculate_take_profit(current_price, signal)

            # Get additional insights
            trend_strength = self.trend_detection_agent.get_trend_strength(data)
            trend_duration = self.trend_detection_agent.get_trend_duration(data)
            volume_trend = self.trend_detection_agent.analyze_volume_trend(data).iloc[-1]
            price_target = self.trend_prediction_agent.predict_price_target(data)

            # Generate the signal dictionary
            signal_dict = {
                "asset": symbol,
                "signal": signal,
                "price": current_price,
                "timestamp": current_timestamp,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "detected_trend": detected_trend,
                "predicted_trend": predicted_trend,
                "trend_strength": trend_strength,
                "trend_duration": trend_duration,
                "volume_trend": "Increasing" if volume_trend == 1 else "Decreasing",
                "price_target": price_target.get('price_target') if price_target else None,
                "price_target_lower": price_target.get('lower_bound') if price_target else None,
                "price_target_upper": price_target.get('upper_bound') if price_target else None
            }

            return signal_dict
        except Exception as e:
            print(f"Error in generate_signal: {str(e)}")
            raise

    def calculate_stop_loss(self, current_price, signal):
        stop_loss_percentage = self.stop_loss_percentages[self.risk_tolerance]
        if signal == "BUY":
            return current_price * (1 - stop_loss_percentage)
        elif signal == "SELL":
            return current_price * (1 + stop_loss_percentage)
        else:
            return None

    def calculate_take_profit(self, current_price, signal):
        take_profit_percentage = self.take_profit_percentages[self.risk_tolerance]
        if signal == "BUY":
            return current_price * (1 + take_profit_percentage)
        elif signal == "SELL":
            return current_price * (1 - take_profit_percentage)
        else:
            return None

    def respond(self, user_input):
        try:
            data = pd.DataFrame(user_input)
            symbol = data.get('symbol', 'Unknown')
            signal = self.generate_signal(data, symbol)
            return f"Signal generated for {symbol}: {signal['signal']} at ${signal['price']:.2f}. " \
                   f"Stop-loss: ${signal['stop_loss']:.2f}, Take-profit: ${signal['take_profit']:.2f}. " \
                   f"Trend: {signal['detected_trend']}, Predicted: {signal['predicted_trend']}"
        except Exception as e:
            return f"Error generating signal: {str(e)}"