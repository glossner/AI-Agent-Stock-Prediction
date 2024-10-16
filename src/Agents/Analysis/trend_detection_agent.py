from src.Agents.base_agent import BaseAgent
import pandas as pd
import numpy as np
import pandas_ta as ta
from pydantic import Field

class TrendDetectionAgent(BaseAgent):
    indicators: dict = Field(default_factory=lambda: {
        'sma': lambda data, window=50: ta.sma(data['Close'], length=window),
        'ema': lambda data, window=20: ta.ema(data['Close'], length=window),
        'macd': lambda data: ta.macd(data['Close']),
        'rsi': lambda data, window=14: ta.rsi(data['Close'], length=window)
    })

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(
            role='Trend Detection Agent',
            goal='Analyze market trends using multiple indicators',
            backstory='Expert in combining various technical indicators for comprehensive trend analysis',
            **data
        )

    def analyze_trend(self, data: pd.DataFrame) -> str:
        try:
            sma = self.indicators['sma'](data)
            ema = self.indicators['ema'](data)
            macd = self.indicators['macd'](data)
            rsi = self.indicators['rsi'](data)

            last_close = data['Close'].iloc[-1]
            sma_last = sma.iloc[-1]
            ema_last = ema.iloc[-1]
            macd_last = macd['MACD_12_26_9'].iloc[-1]
            signal_last = macd['MACDs_12_26_9'].iloc[-1]
            rsi_last = rsi.iloc[-1]

            trend_signals = []

            if last_close > sma_last and last_close > ema_last:
                trend_signals.append(1)
            elif last_close < sma_last and last_close < ema_last:
                trend_signals.append(-1)
            else:
                trend_signals.append(0)

            if macd_last > signal_last:
                trend_signals.append(1)
            elif macd_last < signal_last:
                trend_signals.append(-1)
            else:
                trend_signals.append(0)

            if rsi_last > 70:
                trend_signals.append(-1)
            elif rsi_last < 30:
                trend_signals.append(1)
            else:
                trend_signals.append(0)

            avg_signal = np.mean(trend_signals)

            if avg_signal > 0.3:
                return "Uptrend"
            elif avg_signal < -0.3:
                return "Downtrend"
            else:
                return "Sideways"
        except Exception as e:
            print(f"Error in analyze_trend: {str(e)}")
            return "Unknown"

    def get_trend_strength(self, data: pd.DataFrame) -> float:
        try:
            trend = self.analyze_trend(data)
            rsi = self.indicators['rsi'](data)
            rsi_last = rsi.iloc[-1]

            if trend == "Uptrend":
                return min(rsi_last / 100, 1.0)
            elif trend == "Downtrend":
                return min((100 - rsi_last) / 100, 1.0)
            else:
                return 0.5
        except Exception as e:
            print(f"Error in get_trend_strength: {str(e)}")
            return 0.5

    def get_trend_duration(self, data: pd.DataFrame) -> int:
        try:
            current_trend = self.analyze_trend(data)
            duration = 0
            for i in range(len(data) - 1, -1, -1):
                if self.analyze_trend(data.iloc[:i+1]) == current_trend:
                    duration += 1
                else:
                    break
            return duration
        except Exception as e:
            print(f"Error in get_trend_duration: {str(e)}")
            return 0

    def analyze_volume_trend(self, data: pd.DataFrame) -> pd.Series:
        try:
            volume_sma = ta.sma(data['Volume'], length=20)
            volume_trend = np.where(data['Volume'] > volume_sma, 1, -1)
            return pd.Series(volume_trend, index=data.index)
        except Exception as e:
            print(f"Error in analyze_volume_trend: {str(e)}")
            return pd.Series(index=data.index)

    def construct_message(self, data: pd.DataFrame) -> str:
        trend = self.analyze_trend(data)
        strength = self.get_trend_strength(data)
        duration = self.get_trend_duration(data)
        volume_trend = self.analyze_volume_trend(data).iloc[-1]

        return f"""
        Analyze the following trend data:
        - Current Trend: {trend}
        - Trend Strength: {strength:.2f}
        - Trend Duration: {duration} periods
        - Volume Trend: {"Increasing" if volume_trend == 1 else "Decreasing"}

        Provide insights on the current market trend based on this analysis.
        Consider factors like potential reversals and overall market sentiment.
        Limit your response to 3-4 sentences.
        """

    def respond(self, data: pd.DataFrame) -> str:
        try:
            trend = self.analyze_trend(data)
            strength = self.get_trend_strength(data)
            duration = self.get_trend_duration(data)
            volume_trend = "Increasing" if self.analyze_volume_trend(data).iloc[-1] == 1 else "Decreasing"

            return f"Current Trend: {trend}\nTrend Strength: {strength:.2f}\nTrend Duration: {duration} periods\nVolume Trend: {volume_trend}"
        except Exception as e:
            print(f"Error in respond: {str(e)}")
            return "Unable to analyze trend due to an error."