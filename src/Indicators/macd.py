import pandas as pd

class MACDIndicator:
    def __init__(self, data, short_window=12, long_window=26, signal_window=9):
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window

    def calculate_macd(self):
        """
        Calculates MACD and Signal Line.

        Returns:
            pd.DataFrame: DataFrame with MACD and Signal Line.
        """
        self.data['EMA12'] = self.data['Close'].ewm(span=self.short_window, adjust=False).mean()
        self.data['EMA26'] = self.data['Close'].ewm(span=self.long_window, adjust=False).mean()
        self.data['MACD'] = self.data['EMA12'] - self.data['EMA26']
        self.data['Signal_Line'] = self.data['MACD'].ewm(span=self.signal_window, adjust=False).mean()
        return self.data[['MACD', 'Signal_Line']]
