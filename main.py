from src.backtesting.backtester import Backtester
from src.strategy.rsi_strategy import RSIStrategy
from src.utils.database import Database
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from prettytable import PrettyTable
from datetime import datetime, timedelta

def plot_results(results, asset):
    plt.figure(figsize=(12, 6))
    plt.plot(results['date'], results['portfolio_value'], label='Portfolio Value')
    plt.plot(results['date'], results[f'{asset.lower()}_price'] * (results['portfolio_value'].iloc[0] / results[f'{asset.lower()}_price'].iloc[0]), label=f'{asset.upper()} Price (Normalized)')
    plt.legend()
    plt.title(f'Backtesting Results: Portfolio Value vs {asset.upper()} Price')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.show()

    plt.figure(figsize=(12, 6))
    drawdown = (results['portfolio_value'] / results['portfolio_value'].cummax() - 1)
    plt.plot(results['date'], drawdown)
    plt.fill_between(results['date'], drawdown, 0, alpha=0.3)
    plt.title('Portfolio Drawdown')
    plt.xlabel('Date')
    plt.ylabel('Drawdown')
    plt.show()

    plt.figure(figsize=(12, 6))
    daily_returns = results['portfolio_value'].pct_change()
    sns.histplot(daily_returns, kde=True)
    plt.title('Distribution of Daily Returns')
    plt.xlabel('Daily Return')
    plt.ylabel('Frequency')
    plt.show()

    plt.figure(figsize=(12, 6))
    cumulative_returns = (1 + daily_returns).cumprod()
    plt.plot(results['date'], cumulative_returns)
    plt.title('Cumulative Returns')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.show()

    plt.figure(figsize=(12, 6))
    rolling_sharpe = daily_returns.rolling(window=30).mean() / daily_returns.rolling(window=30).std() * np.sqrt(252)
    plt.plot(results['date'][30:], rolling_sharpe[30:])
    plt.title('30-Day Rolling Sharpe Ratio')
    plt.xlabel('Date')
    plt.ylabel('Sharpe Ratio')
    plt.show()

def print_performance_summary(metrics):
    table = PrettyTable()
    table.field_names = ["Metric", "Value"]
    for key, value in metrics.items():
        table.add_row([key.replace('_', ' ').title(), f"{value:.2%}" if isinstance(value, float) else value])
    print(table)

def create_trade_log(results, asset):
    trades = results[results['portfolio_value'].diff() != 0].copy()
    trades['trade_type'] = np.where(trades['portfolio_value'].diff() > 0, 'Buy', 'Sell')
    trades['trade_return'] = trades['portfolio_value'].pct_change()
    return trades[['date', 'trade_type', f'{asset.lower()}_price', 'portfolio_value', 'trade_return']]

def main():
    try:
        strategy = RSIStrategy(rsi_period=14, overbought=65, oversold=35)
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        
        symbol = "SOL-USD"
        
        backtester = Backtester(strategy, start_date=start_date, end_date=end_date, initial_capital=10000, symbol=symbol, initial_position=0)
        
        results = backtester.run()
        print("Results shape:", results.shape)
        print("Results columns:", results.columns)
        print("First few rows of results:")
        print(results.head())

        metrics = backtester.calculate_metrics(results)

        print("\nBacktesting Results:")
        print_performance_summary(metrics)

        db = Database()
        stored_results = db.get_backtest_results(f"{strategy.__class__.__name__}_{symbol}")
        if stored_results and 'results' in stored_results:
            print("\nRetrieved stored backtest results:")
            stored_df = pd.DataFrame(stored_results['results'])
            print(stored_df.head())
        else:
            print("\nNo stored backtest results found.")
        db.close()

        if not results.empty:
            asset = symbol.split('-')[0].lower()
            plot_results(results, asset)
            
            trade_log = create_trade_log(results, asset)
            print("\nTrade Log:")
            print(trade_log)
        else:
            print("No data to visualize.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()