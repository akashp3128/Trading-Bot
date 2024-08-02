import pandas as pd
import numpy as np
from ..data_collection.exchange_data import get_historical_data
from ..utils.database import Database

class Backtester:
    def __init__(self, strategy, start_date, end_date, initial_capital, symbol="BTC-USD"):
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.symbol = symbol
        self.asset = symbol.split('-')[0]  # Extracts 'BTC' from 'BTC-USD'

    def run(self):
        data = get_historical_data(self.symbol, self.start_date, self.end_date)
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
                self.positions[self.asset] = quantity
                self.current_capital = 0
            elif signal == -1 and self.asset in self.positions:  # Sell signal
                sell_amount = self.positions[self.asset] * row['close']
                self.current_capital = sell_amount
                del self.positions[self.asset]

            portfolio_value = self.current_capital
            if self.asset in self.positions:
                portfolio_value += self.positions[self.asset] * row['close']

            results.append({
                'date': row.name,
                'portfolio_value': portfolio_value,
                f'{self.asset.lower()}_price': row['close']
            })

        results_df = pd.DataFrame(results)
        print(f"Results DataFrame shape: {results_df.shape}")
        print(f"Results DataFrame head:\n{results_df.head()}")
        
        # Store backtest results in MongoDB
        db = Database()
        db.insert_backtest_results(f"{self.strategy.__class__.__name__}_{self.symbol}", results_df)
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

        # Existing calculations
        total_return = (results['portfolio_value'].iloc[-1] - self.initial_capital) / self.initial_capital
        daily_returns = results['portfolio_value'].pct_change()
        sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)  # Annualized
        max_drawdown = (results['portfolio_value'] / results['portfolio_value'].cummax() - 1).min()

        # New metrics
        annualized_return = (1 + total_return) ** (365 / len(results)) - 1
        volatility = daily_returns.std() * np.sqrt(252)
        sortino_ratio = (daily_returns.mean() / daily_returns[daily_returns < 0].std()) * np.sqrt(252)
        
        # Calmar Ratio
        peak = results['portfolio_value'].cummax()
        drawdown = (results['portfolio_value'] - peak) / peak
        calmar_ratio = annualized_return / abs(drawdown.min())

        # Win Rate
        trades = results['portfolio_value'].diff() != 0
        wins = (results['portfolio_value'].diff()[trades] > 0).sum()
        win_rate = wins / trades.sum()

        # Profit Factor
        gains = results['portfolio_value'].diff()[results['portfolio_value'].diff() > 0].sum()
        losses = abs(results['portfolio_value'].diff()[results['portfolio_value'].diff() < 0].sum())
        profit_factor = gains / losses if losses != 0 else float('inf')

        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'max_drawdown': max_drawdown,
            'volatility': volatility,
            'win_rate': win_rate,
            'profit_factor': profit_factor
        }