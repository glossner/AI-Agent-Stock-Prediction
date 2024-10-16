from src.Agents.base_agent import BaseAgent
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from pydantic import Field
from typing import Tuple, Union

class TrendPredictionAgent(BaseAgent):
    arima_model: ARIMA = Field(default=None)
    lstm_model: Sequential = Field(default=None)
    scaler: MinMaxScaler = Field(default_factory=lambda: MinMaxScaler(feature_range=(0, 1)))

    def __init__(self, **data):
        super().__init__(
            role='Trend Prediction Agent',
            goal='Predict future market trends using statistical and machine learning models',
            backstory='Expert in time series analysis and forecasting for financial markets',
            **data
        )

    def predict_trend(self, data: pd.DataFrame, model_type: str = 'arima', forecast_steps: int = 30) -> Tuple[str, float, pd.Series]:
        try:
            if model_type == 'arima':
                return self._predict_arima(data, forecast_steps)
            elif model_type == 'lstm':
                return self._predict_lstm(data, forecast_steps)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
        except Exception as e:
            print(f"Error in {model_type} prediction: {str(e)}")
            return "Unknown", 0.0, pd.Series()

    def _predict_arima(self, data: pd.DataFrame, forecast_steps: int) -> Tuple[str, float, pd.Series]:
        try:
            if self.arima_model is None:
                self._train_arima(data)
            
            # Use the last known index for forecasting
            last_date = data.index[-1]
            forecast = self.arima_model.forecast(steps=forecast_steps)
            forecast_index = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_steps)
            forecast = pd.Series(forecast, index=forecast_index)
            
            last_price = data['Close'].iloc[-1]
            predicted_price = forecast.iloc[0]
            
            trend = "Uptrend" if predicted_price > last_price else "Downtrend"
            confidence = min(abs(predicted_price - last_price) / last_price, 1.0)  # Capped at 1.0
            
            return trend, confidence, forecast
        except Exception as e:
            print(f"Error in ARIMA prediction: {str(e)}")
            return "Unknown", 0.0, pd.Series()

    def _predict_lstm(self, data: pd.DataFrame, forecast_steps: int) -> Tuple[str, float, pd.Series]:
        try:
            if self.lstm_model is None:
                self._train_lstm(data)
            
            scaled_data = self.scaler.transform(data['Close'].values.reshape(-1, 1))
            last_60_days = scaled_data[-60:]
            
            forecast = []
            current_batch = last_60_days
            for _ in range(forecast_steps):
                current_batch = current_batch.reshape((1, 60, 1))
                next_pred = self.lstm_model.predict(current_batch)[0]
                forecast.append(next_pred[0])
                current_batch = np.append(current_batch[:, 1:, :], [[next_pred]], axis=1)
            
            forecast = self.scaler.inverse_transform(np.array(forecast).reshape(-1, 1)).flatten()
            forecast_index = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=forecast_steps)
            forecast = pd.Series(forecast, index=forecast_index)
            
            last_price = data['Close'].iloc[-1]
            predicted_price = forecast.iloc[0]
            
            trend = "Uptrend" if predicted_price > last_price else "Downtrend"
            confidence = min(abs(predicted_price - last_price) / last_price, 1.0)  # Capped at 1.0
            
            return trend, confidence, forecast
        except Exception as e:
            print(f"Error in LSTM prediction: {str(e)}")
            return "Unknown", 0.0, pd.Series()


    def _train_arima(self, data: pd.DataFrame):
        # Resample data to ensure consistent frequency
        data_resampled = data['Close'].resample('D').last().ffill()
        model = ARIMA(data_resampled, order=(5,1,0))
        self.arima_model = model.fit()

    def _train_lstm(self, data: pd.DataFrame):
        scaled_data = self.scaler.fit_transform(data['Close'].values.reshape(-1, 1))
        
        X, y = [], []
        for i in range(60, len(scaled_data)):
            X.append(scaled_data[i-60:i, 0])
            y.append(scaled_data[i, 0])
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)))
        model.add(LSTM(units=50))
        model.add(Dense(1))
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(X, y, epochs=1, batch_size=1, verbose=0)
        
        self.lstm_model = model

    def predict_price_target(self, data: pd.DataFrame) -> dict:
        try:
            last_price = data['Close'].iloc[-1]
            arima_trend, _ = self._predict_arima(data)
            lstm_trend, _ = self._predict_lstm(data)
            
            if arima_trend == lstm_trend == "Uptrend":
                predicted_price = last_price * 1.05
            elif arima_trend == lstm_trend == "Downtrend":
                predicted_price = last_price * 0.95
            else:
                predicted_price = last_price
            
            return {
                'price_target': predicted_price,
                'lower_bound': predicted_price * 0.95,
                'upper_bound': predicted_price * 1.05
            }
        except Exception as e:
            print(f"Error in price target prediction: {str(e)}")
            return {
                'price_target': last_price,
                'lower_bound': last_price * 0.95,
                'upper_bound': last_price * 1.05
            }

    def construct_message(self, data: pd.DataFrame) -> str:
        arima_trend, arima_confidence = self._predict_arima(data)
        lstm_trend, lstm_confidence = self._predict_lstm(data)
        price_target = self.predict_price_target(data)

        return f"""
        Analyze the following trend predictions:
        - ARIMA Prediction: {arima_trend} (Confidence: {arima_confidence:.2f})
        - LSTM Prediction: {lstm_trend} (Confidence: {lstm_confidence:.2f})
        - Price Target: ${price_target['price_target']:.2f} (Range: ${price_target['lower_bound']:.2f} - ${price_target['upper_bound']:.2f})

        Provide insights on the future market trend based on these predictions.
        Consider factors like potential trend reversals and overall market sentiment.
        Limit your response to 3-4 sentences.
        """

    def respond(self, data: pd.DataFrame) -> str:
        try:
            arima_trend, arima_confidence, arima_forecast = self._predict_arima(data, forecast_steps=30)
            lstm_trend, lstm_confidence, lstm_forecast = self._predict_lstm(data, forecast_steps=30)

            response = f"ARIMA Prediction: {arima_trend} (Confidence: {arima_confidence:.2f})\n"
            response += f"LSTM Prediction: {lstm_trend} (Confidence: {lstm_confidence:.2f})\n"
            response += f"ARIMA Forecast (next 30 days): {arima_forecast.iloc[-1]:.2f}\n"
            response += f"LSTM Forecast (next 30 days): {lstm_forecast.iloc[-1]:.2f}"
            
            return response
        except Exception as e:
            print(f"Error in respond: {str(e)}")
            return "Unable to predict trend due to an error."