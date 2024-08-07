import pandas as pd
import numpy as np
from ..data_collection.exchange_data import get_historical_data
from ..utils.database import Database

class Backtester:
    def __init__(self, strategy, start_date, end_date, initial_capital, symbol="BTC-USD", initial_position=0):
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.symbol = symbol
        self.asset = symbol.split('-')[0]
        self.positions = {self.asset: initial_position}
        self.stop_loss_pct = 0.05  # 5% stop loss
        self.take_profit_pct = 0.1  # 10% take profit

    def run(self):
        data = get_historical_data(self.symbol, self.start_date, self.end_date)
        print(f"Historical data shape: {data.shape}")
        print(f"Historical data head:\n{data.head()}")

        if data.empty:
            print("No historical data available. Returning empty results.")
            return pd.DataFrame()

        results = []
        entry_price = None

        for i in range(len(data)):
            current_data = data.iloc[:i+1]
            if len(current_data) >= self.strategy.long_window:
                signal = self.strategy.generate_signal(current_data)
                support, resistance = np.nan, np.nan  # SMACrossoverStrategy doesn't provide support/resistance
            else:
                signal, support, resistance = 0, np.nan, np.nan

            row = data.iloc[i]
            
            # Check for stop loss or take profit
            if entry_price is not None:
                if signal != 1:  # We're in a position
                    if row['close'] <= entry_price * (1 - self.stop_loss_pct):
                        print("Stop Loss triggered")
                        signal = -1
                    elif row['close'] >= entry_price * (1 + self.take_profit_pct):
                        print("Take Profit triggered")
                        signal = -1

            if signal == 1:  # Buy signal
                buy_amount = min(self.current_capital, self.initial_capital * 0.8)
                if buy_amount > 0:
                    quantity = buy_amount / row['close']
                    self.positions[self.asset] = self.positions.get(self.asset, 0) + quantity
                    self.current_capital -= buy_amount
                    entry_price = row['close']
            elif signal == -1:  # Sell signal
                sell_quantity = min(self.positions.get(self.asset, 0), self.positions.get(self.asset, 0) * 0.8)
                if sell_quantity > 0:
                    sell_amount = sell_quantity * row['close']
                    self.positions[self.asset] -= sell_quantity
                    self.current_capital += sell_amount
                    entry_price = None

            portfolio_value = self.current_capital + self.positions.get(self.asset, 0) * row['close']

            results.append({
                'date': row.name,
                'portfolio_value': portfolio_value,
                f'{self.asset.lower()}_price': row['close'],
                'position': self.positions.get(self.asset, 0),
                'support': support,
                'resistance': resistance
            })

        results_df = pd.DataFrame(results)
        print(f"Results DataFrame shape: {results_df.shape}")
        print(f"Results DataFrame head:\n{results_df.head()}")
        
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

        total_return = (results['portfolio_value'].iloc[-1] - self.initial_capital) / self.initial_capital
        daily_returns = results['portfolio_value'].pct_change()
        sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)  # Annualized
        max_drawdown = (results['portfolio_value'] / results['portfolio_value'].cummax() - 1).min()

        annualized_return = (1 + total_return) ** (365 / len(results)) - 1
        volatility = daily_returns.std() * np.sqrt(252)
        sortino_ratio = (daily_returns.mean() / daily_returns[daily_returns < 0].std()) * np.sqrt(252)
        
        peak = results['portfolio_value'].cummax()
        drawdown = (results['portfolio_value'] - peak) / peak
        calmar_ratio = annualized_return / abs(drawdown.min()) if drawdown.min() != 0 else np.inf

        trades = results['portfolio_value'].diff() != 0
        wins = (results['portfolio_value'].diff()[trades] > 0).sum()
        win_rate = wins / trades.sum() if trades.sum() > 0 else 0

        gains = results['portfolio_value'].diff()[results['portfolio_value'].diff() > 0].sum()
        losses = abs(results['portfolio_value'].diff()[results['portfolio_value'].diff() < 0].sum())
        profit_factor = gains / losses if losses != 0 else np.inf

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