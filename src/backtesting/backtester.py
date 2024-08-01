import pandas as pd
import numpy as np
from ..data_collection.exchange_data import get_historical_data
from ..utils.database import Database

class Backtester:
    def __init__(self, strategy, start_date, end_date, initial_capital):
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}

    def run(self):
        data = get_historical_data("BTC-USD", self.start_date, self.end_date)
        print(f"Historical data shape: {data.shape}")
        print(f"Historical data head:\n{data.head()}")

        if data.empty:
            print("No historical data available. Returning empty results.")
            return pd.DataFrame()

        results = []

        for i in range(len(data)):
            current_data = data.iloc[:i+1]
            if len(current_data) >= self.strategy.long_window:
                signal = self.strategy.generate_signal(current_data)
            else:
                signal = 0

            row = data.iloc[i]
            if signal == 1 and self.current_capital > 0:  # Buy signal
                buy_amount = self.current_capital
                quantity = buy_amount / row['close']
                self.positions['BTC'] = quantity
                self.current_capital = 0
            elif signal == -1 and 'BTC' in self.positions:  # Sell signal
                sell_amount = self.positions['BTC'] * row['close']
                self.current_capital = sell_amount
                del self.positions['BTC']

            portfolio_value = self.current_capital
            if 'BTC' in self.positions:
                portfolio_value += self.positions['BTC'] * row['close']

            results.append({
                'date': row.name,
                'portfolio_value': portfolio_value,
                'btc_price': row['close']
            })

        results_df = pd.DataFrame(results)
        print(f"Results DataFrame shape: {results_df.shape}")
        print(f"Results DataFrame head:\n{results_df.head()}")
        
        # Store backtest results in MongoDB
        db = Database()
        db.insert_backtest_results(self.strategy.__class__.__name__, results_df)
        db.close()
        
        return results_df

    def calculate_metrics(self, results):
        if results.empty:
            print("No results to calculate metrics. Returning empty metrics.")
            return {
                'total_return': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            }

        total_return = (results['portfolio_value'].iloc[-1] - self.initial_capital) / self.initial_capital
        daily_returns = results['portfolio_value'].pct_change()
        sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)  # Annualized
        max_drawdown = (results['portfolio_value'] / results['portfolio_value'].cummax() - 1).min()

        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown
        }