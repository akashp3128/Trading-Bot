from src.backtesting.backtester import Backtester
from src.strategy.simple_moving_average import SMACrossoverStrategy
from src.utils.database import Database
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

def main():
    try:
        strategy = SMACrossoverStrategy(short_window=10, long_window=30)
        
        # Use a 6-month date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        
        backtester = Backtester(strategy, start_date=start_date, end_date=end_date, initial_capital=10000)
        
        results = backtester.run()
        print("Results shape:", results.shape)
        print("Results columns:", results.columns)
        print("First few rows of results:")
        print(results.head())

        metrics = backtester.calculate_metrics(results)

        print("\nBacktesting Results:")
        print(f"Total Return: {metrics['total_return']:.2%}")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")

        # Retrieve stored results from MongoDB
        db = Database()
        stored_results = db.get_backtest_results(strategy.__class__.__name__)
        if stored_results and 'results' in stored_results:
            print("\nRetrieved stored backtest results:")
            stored_df = pd.DataFrame(stored_results['results'])
            print(stored_df.head())
        else:
            print("\nNo stored backtest results found.")
        db.close()

        if not results.empty:
            # Visualize results
            plt.figure(figsize=(12, 6))
            plt.plot(results['date'], results['portfolio_value'], label='Portfolio Value')
            plt.plot(results['date'], results['btc_price'] * (10000 / results['btc_price'].iloc[0]), label='BTC Price (Normalized)')
            plt.legend()
            plt.title('Backtesting Results: Portfolio Value vs BTC Price')
            plt.xlabel('Date')
            plt.ylabel('Value')
            plt.show()
        else:
            print("No data to visualize.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()