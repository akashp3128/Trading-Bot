import pandas as pd

def sma_crossover_strategy(df, short_window=10, long_window=30):
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()
    df['signal'] = 0
    df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1
    df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1
    return df

# Usage
# df_with_signals = sma_crossover_strategy(processed_data)