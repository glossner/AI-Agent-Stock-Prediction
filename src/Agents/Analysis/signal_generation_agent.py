from src.Agents.base_agent import BaseAgent
from src.Agents.Analysis.trend_detection_agent import TrendDetectionAgent
from src.Agents.Analysis.trend_prediction_agent import TrendPredictionAgent
import pandas as pd
import numpy as np
from datetime import datetime
from pydantic import Field

class SignalGenerationAgent(BaseAgent):
    trend_detection_agent: TrendDetectionAgent = Field(default_factory=TrendDetectionAgent)
    trend_prediction_agent: TrendPredictionAgent = Field(default_factory=TrendPredictionAgent)
    risk_tolerance: str = Field(default='medium')
    stop_loss_percentages: dict = Field(default_factory=lambda: {'low': 0.02, 'medium': 0.05, 'high': 0.10})
    take_profit_percentages: dict = Field(default_factory=lambda: {'low': 0.03, 'medium': 0.08, 'high': 0.15})

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(
            role='Signal Generation Agent',
            goal='Generate clear and actionable buy/sell signals based on trend analysis',
            backstory='Expert in synthesizing market trends and predictions to generate trading signals',
            **data
        )

    def generate_signal(self, data: pd.DataFrame, symbol: str) -> dict:
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input data must be a pandas DataFrame")
        
        if 'Close' not in data.columns:
            raise ValueError("DataFrame must contain a 'Close' column")

        current_price = data['Close'].iloc[-1]
        current_timestamp = data.index[-1]

        try:
            # Get trend from TrendDetectionAgent
            detected_trend = self.trend_detection_agent.analyze_trend(data)
            trend_strength = self.trend_detection_agent.get_trend_strength(data)
            trend_duration = self.trend_detection_agent.get_trend_duration(data)

            # Get prediction from TrendPredictionAgent
            predicted_trend, confidence = self.trend_prediction_agent.predict_trend(data, model_type='arima')

            # Define signal criteria
            signal = self.determine_signal(detected_trend, predicted_trend, trend_strength, confidence)

            # Calculate risk management levels
            stop_loss = self.calculate_stop_loss(current_price, signal)
            take_profit = self.calculate_take_profit(current_price, signal)

            # Get additional insights
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
                "prediction_confidence": confidence,
                "volume_trend": "Increasing" if volume_trend == 1 else "Decreasing",
                "price_target": price_target.get('price_target', current_price),
                "price_target_lower": price_target.get('lower_bound', current_price * 0.95),
                "price_target_upper": price_target.get('upper_bound', current_price * 1.05)
            }

            return signal_dict
        except Exception as e:
            print(f"Error in generate_signal: {str(e)}")
            # Return a default signal in case of error
            return {
                "asset": symbol,
                "signal": "HOLD",
                "price": current_price,
                "timestamp": current_timestamp,
                "stop_loss": None,
                "take_profit": None,
                "detected_trend": "Unknown",
                "predicted_trend": "Unknown",
                "trend_strength": 0,
                "trend_duration": 0,
                "prediction_confidence": 0,
                "volume_trend": "Unknown",
                "price_target": current_price,
                "price_target_lower": current_price * 0.95,
                "price_target_upper": current_price * 1.05
            }

    def determine_signal(self, detected_trend, predicted_trend, trend_strength, prediction_confidence):
        # Define criteria for generating buy/sell signals
        if detected_trend == "Uptrend" and predicted_trend == "Uptrend" and trend_strength > 0.7 and prediction_confidence > 0.8:
            return "STRONG BUY"
        elif detected_trend == "Uptrend" and predicted_trend == "Uptrend" and trend_strength > 0.5:
            return "BUY"
        elif detected_trend == "Downtrend" and predicted_trend == "Downtrend" and trend_strength > 0.7 and prediction_confidence > 0.8:
            return "STRONG SELL"
        elif detected_trend == "Downtrend" and predicted_trend == "Downtrend" and trend_strength > 0.5:
            return "SELL"
        else:
            return "HOLD"

    def calculate_stop_loss(self, current_price, signal):
        stop_loss_percentage = self.stop_loss_percentages[self.risk_tolerance]
        if "BUY" in signal:
            return round(current_price * (1 - stop_loss_percentage), 2)
        elif "SELL" in signal:
            return round(current_price * (1 + stop_loss_percentage), 2)
        else:
            return None

    def calculate_take_profit(self, current_price, signal):
        take_profit_percentage = self.take_profit_percentages[self.risk_tolerance]
        if "BUY" in signal:
            return round(current_price * (1 + take_profit_percentage), 2)
        elif "SELL" in signal:
            return round(current_price * (1 - take_profit_percentage), 2)
        else:
            return None

    def respond(self, user_input: pd.DataFrame) -> str:
        try:
            symbol = user_input.get('symbol', 'Unknown')
            signal = self.generate_signal(user_input, symbol)
            return self.format_signal_response(signal)
        except Exception as e:
            return f"Error generating signal: {str(e)}"

    def format_signal_response(self, signal: dict) -> str:
        response = f"Signal for {signal['asset']}: {signal['signal']}\n"
        response += f"Price: ${signal['price']:.2f} at {signal['timestamp']}\n"
        if signal['stop_loss']:
            response += f"Stop-loss: ${signal['stop_loss']:.2f}\n"
        if signal['take_profit']:
            response += f"Take-profit: ${signal['take_profit']:.2f}\n"
        response += f"Detected Trend: {signal['detected_trend']} (Strength: {signal['trend_strength']:.2f}, Duration: {signal['trend_duration']} periods)\n"
        response += f"Predicted Trend: {signal['predicted_trend']}"
        if signal['prediction_confidence']:
            response += f" (Confidence: {signal['prediction_confidence']:.2f})\n"
        else:
            response += "\n"
        response += f"Volume Trend: {signal['volume_trend']}\n"
        if signal['price_target']:
            response += f"Price Target: ${signal['price_target']:.2f} "
            if signal['price_target_lower'] and signal['price_target_upper']:
                response += f"(Range: ${signal['price_target_lower']:.2f} - ${signal['price_target_upper']:.2f})"
        return response

    def construct_message(self, data: pd.DataFrame) -> str:
        # Implement if needed for OpenAI API calls
        pass