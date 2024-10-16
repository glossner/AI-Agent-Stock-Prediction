import pandas as pd
import numpy as np
import pandas_ta as ta
import logging

logger = logging.getLogger(__name__)

class TrendDetectionAgent:
    def __init__(self):
        self.indicators = {
            'sma': self.calculate_sma,
            'ema': self.calculate_ema,
            'macd': self.calculate_macd,
            'rsi': self.calculate_rsi
        }

    def calculate_sma(self, data, window=50):
        try:
            if len(data) < window:
                logger.warning(f"Not enough data points for SMA calculation. Required: {window}, Available: {len(data)}")
                return None
            return ta.sma(data['Close'], length=window)
        except Exception as e:
            logger.error(f"Error calculating SMA: {str(e)}")
            return None

    def calculate_ema(self, data, window=20):
        try:
            if len(data) < window:
                logger.warning(f"Not enough data points for EMA calculation. Required: {window}, Available: {len(data)}")
                return None
            return ta.ema(data['Close'], length=window)
        except Exception as e:
            logger.error(f"Error calculating EMA: {str(e)}")
            return None

    def calculate_macd(self, data):
        try:
            if len(data) < 26:  # Minimum required for MACD
                logger.warning(f"Not enough data points for MACD calculation. Required: 26, Available: {len(data)}")
                return None, None
            macd = ta.macd(data['Close'])
            return macd['MACD_12_26_9'], macd['MACDs_12_26_9']
        except Exception as e:
            logger.error(f"Error calculating MACD: {str(e)}")
            return None, None

    def calculate_rsi(self, data, window=14):
        try:
            if len(data) < window:
                logger.warning(f"Not enough data points for RSI calculation. Required: {window}, Available: {len(data)}")
                return None
            return ta.rsi(data['Close'], length=window)
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return None

    def detect_trend(self, data, method='sma'):
        if not isinstance(data, pd.DataFrame) or data.empty:
            logger.error("Invalid or empty DataFrame")
            return pd.Series(index=data.index if isinstance(data, pd.DataFrame) else pd.Index([]))

        if 'Close' not in data.columns:
            logger.error("DataFrame must contain a 'Close' column")
            return pd.Series(index=data.index)

        if method not in self.indicators:
            logger.error(f"Invalid trend detection method: {method}")
            return pd.Series(index=data.index)

        indicator = self.indicators[method](data)

        if indicator is None:
            logger.warning(f"Indicator calculation failed for method: {method}")
            return pd.Series(index=data.index)

        if method in ['sma', 'ema']:
            trend = np.where(data['Close'] > indicator, 1, -1)
        elif method == 'macd':
            macd, signal = indicator
            if macd is None or signal is None:
                return pd.Series(index=data.index)
            trend = np.where(macd > signal, 1, -1)
        elif method == 'rsi':
            trend = np.where(indicator > 70, -1, np.where(indicator < 30, 1, 0))
        else:
            trend = np.zeros(len(data))

        return pd.Series(trend, index=data.index)

    def analyze_trend(self, data, methods=['sma', 'ema', 'macd', 'rsi']):
        if not isinstance(data, pd.DataFrame) or data.empty:
            logger.error("Invalid or empty DataFrame")
            return "Indeterminate"

        trends = {}
        for method in methods:
            trend = self.detect_trend(data, method)
            if not trend.empty and not trend.isnull().all():
                trends[method] = trend

        if not trends:
            logger.warning("No valid trends detected")
            return "Indeterminate"

        combined_trend = pd.DataFrame(trends)
        if combined_trend.empty:
            logger.warning("Combined trend DataFrame is empty")
            return "Indeterminate"
        
        mode_result = combined_trend.mode(axis=1)
        if mode_result.empty or mode_result.iloc[-1].empty:
            logger.warning("Mode calculation resulted in empty DataFrame")
            return "Indeterminate"
        
        last_trend = mode_result.iloc[-1, 0]
        if last_trend == 1:
            return "Uptrend"
        elif last_trend == -1:
            return "Downtrend"
        else:
            return "Sideways"

    def get_trend_strength(self, data, method='sma'):
        trend = self.detect_trend(data, method)
        if trend.empty:
            return 0
        return abs(trend.mean())

    def get_trend_duration(self, data, method='sma'):
        trend = self.detect_trend(data, method)
        if trend.empty:
            return 0
        current_trend = trend.iloc[-1]
        duration = 0
        for i in range(len(trend) - 1, -1, -1):
            if trend.iloc[i] == current_trend:
                duration += 1
            else:
                break
        return duration

    def analyze_volume_trend(self, data):
        if 'Volume' not in data.columns:
            logger.error("DataFrame must contain a 'Volume' column")
            return pd.Series(index=data.index)
        volume_sma = ta.sma(data['Volume'], length=20)
        volume_trend = np.where(data['Volume'] > volume_sma, 1, -1)
        return pd.Series(volume_trend, index=data.index)

    def detect_trend_breakout(self, data, window=20):
        sma = self.calculate_sma(data, window)
        if sma is None:
            return pd.Series(index=data.index)
        breakout_up = (data['Close'] > sma) & (data['Close'].shift(1) <= sma.shift(1))
        breakout_down = (data['Close'] < sma) & (data['Close'].shift(1) >= sma.shift(1))
        return pd.Series(np.where(breakout_up, 1, np.where(breakout_down, -1, 0)), index=data.index)

    def get_trend_reversal_points(self, data, method='sma'):
        trend = self.detect_trend(data, method)
        reversal_points = []
        for i in range(1, len(trend)):
            if trend.iloc[i] != trend.iloc[i-1]:
                reversal_points.append(data.index[i])
        return reversal_points

    def analyze_multiple_timeframes(self, data, timeframes=['1D', '1W', '1M']):
        trends = {}
        for timeframe in timeframes:
            resampled_data = data.resample(timeframe).agg({
                'Open': 'first', 
                'High': 'max', 
                'Low': 'min', 
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            if not resampled_data.empty:
                trends[timeframe] = self.analyze_trend(resampled_data)
            else:
                trends[timeframe] = "Insufficient data"
        return trends