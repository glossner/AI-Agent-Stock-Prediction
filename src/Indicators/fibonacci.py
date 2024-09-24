import pandas as pd

class FibonacciRetracement:
    def __init__(self, data):
        self.data = data

    def calculate_levels(self):
        max_price = self.data['High'].max()
        min_price = self.data['Low'].min()

        difference = max_price - min_price

        # Fibonacci Retracement Levels
        level_0 = max_price
        level_236 = max_price - 0.236 * difference
        level_382 = max_price - 0.382 * difference
        level_50 = max_price - 0.5 * difference
        level_618 = max_price - 0.618 * difference
        level_100 = min_price

        levels = {
            '0%': level_0,
            '23.6%': level_236,
            '38.2%': level_382,
            '50%': level_50,
            '61.8%': level_618,
            '100%': level_100
        }

        return levels
