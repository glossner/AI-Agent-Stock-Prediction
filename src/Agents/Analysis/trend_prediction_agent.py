import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

class TrendPredictionAgent:
    def __init__(self):
        self.arima_model = None
        self.lstm_model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def prepare_data(self, data, sequence_length=60):
        # Check for 'close' or 'Close' column
        if 'close' in data.columns:
            close_column = 'close'
        elif 'Close' in data.columns:
            close_column = 'Close'
        else:
            raise ValueError("No 'close' or 'Close' column found in the data")

        # Prepare data for ARIMA
        arima_data = data[close_column].values

        # Prepare data for LSTM
        scaled_data = self.scaler.fit_transform(data[close_column].values.reshape(-1, 1))
        
        x_lstm, y_lstm = [], []
        for i in range(len(scaled_data) - sequence_length):
            x_lstm.append(scaled_data[i:(i + sequence_length), 0])
            y_lstm.append(scaled_data[i + sequence_length, 0])
        
        x_lstm, y_lstm = np.array(x_lstm), np.array(y_lstm)
        x_lstm = np.reshape(x_lstm, (x_lstm.shape[0], x_lstm.shape[1], 1))

        return arima_data, x_lstm, y_lstm

    def train_arima(self, data):
        arima_data, _, _ = self.prepare_data(data)
        self.arima_model = ARIMA(arima_data, order=(5,1,0))
        self.arima_model = self.arima_model.fit()
        return self.arima_model

    def train_lstm(self, data, epochs=50, batch_size=32):
        _, x_lstm, y_lstm = self.prepare_data(data)
        
        self.lstm_model = Sequential()
        self.lstm_model.add(LSTM(units=50, return_sequences=True, input_shape=(x_lstm.shape[1], 1)))
        self.lstm_model.add(LSTM(units=50))
        self.lstm_model.add(Dense(1))

        self.lstm_model.compile(optimizer='adam', loss='mean_squared_error')
        self.lstm_model.fit(x_lstm, y_lstm, epochs=epochs, batch_size=batch_size)
        
        return self.lstm_model

    def predict_trend(self, data, model_type='arima', future_steps=30):
        if 'close' in data.columns:
            close_column = 'close'
        elif 'Close' in data.columns:
            close_column = 'Close'
        else:
            raise ValueError("No 'close' or 'Close' column found in the data")

        if model_type == 'arima':
            if self.arima_model is None:
                self.train_arima(data)
            forecast = self.arima_model.forecast(steps=future_steps)
            predicted_trend = 'Uptrend' if forecast[-1] > data[close_column].iloc[-1] else 'Downtrend'
            return predicted_trend, forecast
        elif model_type == 'lstm':
            if self.lstm_model is None:
                self.train_lstm(data)
            _, x_lstm, _ = self.prepare_data(data)
            last_sequence = x_lstm[-1].reshape(1, x_lstm.shape[1], 1)
            predicted_prices = []
            for _ in range(future_steps):
                price = self.lstm_model.predict(last_sequence)
                predicted_prices.append(price[0, 0])
                last_sequence = np.roll(last_sequence, -1, axis=1)
                last_sequence[0, -1, 0] = price[0, 0]
            predicted_prices = self.scaler.inverse_transform(np.array(predicted_prices).reshape(-1, 1)).flatten()
            predicted_trend = 'Uptrend' if predicted_prices[-1] > data[close_column].iloc[-1] else 'Downtrend'
            return predicted_trend, predicted_prices
        else:
            raise ValueError("Invalid model type. Choose 'arima' or 'lstm'.")

    def evaluate_model(self, data, model_type='arima'):
        if 'close' in data.columns:
            close_column = 'close'
        elif 'Close' in data.columns:
            close_column = 'Close'
        else:
            raise ValueError("No 'close' or 'Close' column found in the data")

        train_size = int(len(data) * 0.8)
        train, test = data[:train_size], data[train_size:]
        
        if model_type == 'arima':
            self.train_arima(train)
            predictions = self.arima_model.forecast(steps=len(test))
        elif model_type == 'lstm':
            self.train_lstm(train)
            _, x_lstm, _ = self.prepare_data(data)
            predictions = self.lstm_model.predict(x_lstm[-len(test):])
            predictions = self.scaler.inverse_transform(predictions).flatten()
        else:
            raise ValueError("Invalid model type. Choose 'arima' or 'lstm'.")
        
        mse = mean_squared_error(test[close_column], predictions)
        rmse = np.sqrt(mse)
        
        plt.figure(figsize=(12,6))
        plt.plot(test.index, test[close_column], label='Actual')
        plt.plot(test.index, predictions, label='Predicted')
        plt.legend()
        plt.title(f'{model_type.upper()} Model Evaluation')
        plt.show()
        
        return rmse

    def optimize_model(self, data, model_type='arima'):
        if 'close' in data.columns:
            close_column = 'close'
        elif 'Close' in data.columns:
            close_column = 'Close'
        else:
            raise ValueError("No 'close' or 'Close' column found in the data")

        if model_type == 'arima':
            best_order = None
            best_aic = np.inf
            for p in range(0, 5):
                for d in range(0, 2):
                    for q in range(0, 5):
                        try:
                            model = ARIMA(data[close_column], order=(p, d, q))
                            results = model.fit()
                            if results.aic < best_aic:
                                best_aic = results.aic
                                best_order = (p, d, q)
                        except:
                            continue
            self.arima_model = ARIMA(data[close_column], order=best_order).fit()
            return best_order
        elif model_type == 'lstm':
            best_params = None
            best_rmse = np.inf
            for units in [32, 64, 128]:
                for batch_size in [16, 32, 64]:
                    for epochs in [50, 100]:
                        self.lstm_model = Sequential()
                        self.lstm_model.add(LSTM(units=units, return_sequences=True, input_shape=(60, 1)))
                        self.lstm_model.add(LSTM(units=units))
                        self.lstm_model.add(Dense(1))
                        self.lstm_model.compile(optimizer='adam', loss='mean_squared_error')
                        
                        _, x_lstm, y_lstm = self.prepare_data(data)
                        self.lstm_model.fit(x_lstm, y_lstm, epochs=epochs, batch_size=batch_size, verbose=0)
                        
                        rmse = self.evaluate_model(data, model_type='lstm')
                        if rmse < best_rmse:
                            best_rmse = rmse
                            best_params = {'units': units, 'batch_size': batch_size, 'epochs': epochs}
            
            self.train_lstm(data, epochs=best_params['epochs'], batch_size=best_params['batch_size'])
            return best_params
        else:
            raise ValueError("Invalid model type. Choose 'arima' or 'lstm'.")