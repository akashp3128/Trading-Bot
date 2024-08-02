import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from prettytable import PrettyTable

def plot_results(results, asset):
    # Portfolio Value vs Asset Price
    plt.figure(figsize=(12, 6))
    plt.plot(results['date'], results['portfolio_value'], label='Portfolio Value')
    plt.plot(results['date'], results[f'{asset}_price'] * (10000 / results[f'{asset}_price'].iloc[0]), label=f'{asset.upper()} Price (Normalized)')
    plt.legend()
    plt.title(f'Backtesting Results: Portfolio Value vs {asset.upper()} Price')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.show()

    # Drawdown plot
    plt.figure(figsize=(12, 6))
    drawdown = (results['portfolio_value'] / results['portfolio_value'].cummax() - 1)
    plt.plot(results['date'], drawdown)
    plt.fill_between(results['date'], drawdown, 0, alpha=0.3)
    plt.title('Portfolio Drawdown')
    plt.xlabel('Date')
    plt.ylabel('Drawdown')
    plt.show()

    # Daily returns distribution
    plt.figure(figsize=(12, 6))
    daily_returns = results['portfolio_value'].pct_change()
    sns.histplot(daily_returns, kde=True)
    plt.title('Distribution of Daily Returns')
    plt.xlabel('Daily Return')
    plt.ylabel('Frequency')
    plt.show()

    # Cumulative returns
    plt.figure(figsize=(12, 6))
    cumulative_returns = (1 + daily_returns).cumprod()
    plt.plot(results['date'], cumulative_returns)
    plt.title('Cumulative Returns')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.show()

    # Rolling Sharpe ratio
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
    return trades[['date', 'trade_type', f'{asset}_price', 'portfolio_value', 'trade_return']]