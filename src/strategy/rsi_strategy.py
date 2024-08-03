import pandas as pd
import numpy as np

class RSIStrategy:
    def __init__(self, rsi_period=14, overbought=65, oversold=35):
        self.rsi_period = rsi_period
        self.overbought = overbought
        self.oversold = oversold

    def calculate_rsi(self, data):
        close_delta = data['close'].diff()

        # Make two series: one for lower closes and one for higher closes
        up = close_delta.clip(lower=0)
        down = -1 * close_delta.clip(upper=0)
        
        # Calculate the EWMA
        ma_up = up.ewm(com = self.rsi_period - 1, adjust=False).mean()
        ma_down = down.ewm(com = self.rsi_period - 1, adjust=False).mean()

        rsi = ma_up / ma_down
        rsi = 100 - (100/(1 + rsi))

        return rsi

    def generate_signal(self, data):
        rsi = self.calculate_rsi(data)
        
        print(f"Latest RSI: {rsi.iloc[-1]:.2f}")
        
        if rsi.iloc[-2] > self.oversold and rsi.iloc[-1] <= self.oversold:
            print("Buy Signal Generated")
            return 1
        elif rsi.iloc[-2] < self.overbought and rsi.iloc[-1] >= self.overbought:
            print("Sell Signal Generated")
            return -1
        else:
            return 0

    @property
    def long_window(self):
        return self.rsi_period