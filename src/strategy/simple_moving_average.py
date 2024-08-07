import pandas as pd
import numpy as np

class SMACrossoverStrategy:
    def __init__(self, short_window, long_window):
        self.short_window = short_window
        self._long_window = long_window  # Use an underscore to indicate it's a private attribute

    def generate_signal(self, data):
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0
        signals['short_mavg'] = data['close'].rolling(window=self.short_window, min_periods=1, center=False).mean()
        signals['long_mavg'] = data['close'].rolling(window=self._long_window, min_periods=1, center=False).mean()
        # Use boolean indexing instead of .loc or .iloc
        signals['signal'] = 0.0
        signals['signal'] = np.where(signals['short_mavg'] > signals['long_mavg'], 1.0, 0.0)
        signals['positions'] = signals['signal'].diff()
        return signals['positions'].iloc[-1]

    @property
    def long_window(self):
        return self._long_window