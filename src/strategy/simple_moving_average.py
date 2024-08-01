import pandas as pd
import numpy as np

class SMACrossoverStrategy:
    def __init__(self, short_window, long_window):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, data):
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        signals['short_mavg'] = data['close'].rolling(window=self.short_window, min_periods=1, center=False).mean()
        signals['long_mavg'] = data['close'].rolling(window=self.long_window, min_periods=1, center=False).mean()

        signals['signal'][self.short_window:] = np.where(signals['short_mavg'][self.short_window:] 
                                                         > signals['long_mavg'][self.short_window:], 1.0, 0.0)   
        signals['positions'] = signals['signal'].diff()

        return signals['positions'].iloc[-1]