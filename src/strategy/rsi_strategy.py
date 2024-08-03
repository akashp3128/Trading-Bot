import pandas as pd
import numpy as np

class RSIStrategy:
    def __init__(self, rsi_period=14, overbought=70, oversold=30, support_resistance_periods=21):
        self.rsi_period = rsi_period
        self.overbought = overbought
        self.oversold = oversold
        self.support_resistance_periods = support_resistance_periods

    def calculate_rsi(self, data):
        close_delta = data['close'].diff()
        up = close_delta.clip(lower=0)
        down = -1 * close_delta.clip(upper=0)
        ma_up = up.ewm(com=self.rsi_period - 1, adjust=False).mean()
        ma_down = down.ewm(com=self.rsi_period - 1, adjust=False).mean()
        rsi = ma_up / ma_down
        rsi = 100 - (100/(1 + rsi))
        return rsi

    def calculate_support_resistance(self, data):
        high_max = data['high'].rolling(window=self.support_resistance_periods).max()
        low_min = data['low'].rolling(window=self.support_resistance_periods).min()
        
        resistance = high_max.shift(1)
        support = low_min.shift(1)
        
        return support, resistance

    def generate_signal(self, data):
        rsi = self.calculate_rsi(data)
        support, resistance = self.calculate_support_resistance(data)
        
        latest_close = data['close'].iloc[-1]
        latest_rsi = rsi.iloc[-1]
        latest_support = support.iloc[-1]
        latest_resistance = resistance.iloc[-1]
        
        print(f"Latest RSI: {latest_rsi:.2f}, Close: {latest_close:.2f}, Support: {latest_support:.2f}, Resistance: {latest_resistance:.2f}")
        
        signal = 0
        if latest_rsi <= self.oversold and latest_close <= latest_support:
            print("Buy Signal Generated")
            signal = 1
        elif latest_rsi >= self.overbought and latest_close >= latest_resistance:
            print("Sell Signal Generated")
            signal = -1
        
        return signal, latest_support, latest_resistance

    @property
    def long_window(self):
        return max(self.rsi_period, self.support_resistance_periods)