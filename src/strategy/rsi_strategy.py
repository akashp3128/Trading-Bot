import pandas as pd
import numpy as np
from ta.trend import MACD
from ta.volatility import BollingerBands

class RSIStrategy:
    def __init__(self, rsi_period=14, overbought=70, oversold=30, support_resistance_periods=21,
                 macd_fast=12, macd_slow=26, macd_signal=9, bb_period=20, bb_std=2):
        self.rsi_period = rsi_period
        self.overbought = overbought
        self.oversold = oversold
        self.support_resistance_periods = support_resistance_periods
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.bb_period = bb_period
        self.bb_std = bb_std

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

    def calculate_indicators(self, data):
        rsi = self.calculate_rsi(data)
        support, resistance = self.calculate_support_resistance(data)
        macd = MACD(close=data['close'], window_slow=self.macd_slow, window_fast=self.macd_fast, window_sign=self.macd_signal)
        bb = BollingerBands(close=data['close'], window=self.bb_period, window_dev=self.bb_std)
        return rsi, support, resistance, macd, bb

    def generate_signal(self, data):
        rsi, support, resistance, macd, bb = self.calculate_indicators(data)
        
        latest_close = data['close'].iloc[-1]
        latest_rsi = rsi.iloc[-1]
        latest_support = support.iloc[-1]
        latest_resistance = resistance.iloc[-1]
        latest_macd = macd.macd().iloc[-1]
        latest_macd_signal = macd.macd_signal().iloc[-1]
        latest_bb_lower = bb.bollinger_lband().iloc[-1]
        latest_bb_upper = bb.bollinger_hband().iloc[-1]
        
        print(f"Latest RSI: {latest_rsi:.2f}, Close: {latest_close:.2f}, Support: {latest_support:.2f}, Resistance: {latest_resistance:.2f}")
        print(f"MACD: {latest_macd:.2f}, Signal: {latest_macd_signal:.2f}, BB Lower: {latest_bb_lower:.2f}, BB Upper: {latest_bb_upper:.2f}")
        
        signal = 0
        if (latest_rsi <= self.oversold and 
            latest_close <= latest_support and
            latest_macd > latest_macd_signal and 
            latest_close <= latest_bb_lower):
            print("Buy Signal Generated")
            signal = 1
        elif (latest_rsi >= self.overbought and 
              latest_close >= latest_resistance and
              latest_macd < latest_macd_signal and 
              latest_close >= latest_bb_upper):
            print("Sell Signal Generated")
            signal = -1
        
        return signal, latest_support, latest_resistance

    @property
    def long_window(self):
        return max(self.rsi_period, self.support_resistance_periods, self.macd_slow, self.bb_period)