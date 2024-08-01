# Cryptocurrency Trading Bot

This project implements a simple cryptocurrency trading bot with backtesting capabilities. It fetches historical price data from the Coinbase Pro API, applies a Simple Moving Average (SMA) crossover strategy, and simulates trading performance.

## Features

- Fetch historical OHLCV data from Coinbase Pro API
- Implement a Simple Moving Average (SMA) crossover strategy
- Backtest trading strategies using historical data
- Calculate performance metrics (Total Return, Sharpe Ratio, Max Drawdown)
- Visualize backtesting results


## Setup and Installation

1. Clone this repository:

2. Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate

3. Install the required packages:
pip install -r requirements.txt

## Usage

Run the main script to perform backtesting:

python main.py

This will execute the SMA crossover strategy on BTC/USD data for the last 6 months and display the results.

## Customisation

- Modify the `SMACrossoverStrategy` class in `src/strategy/simple_moving_average.py` to implement different trading strategies.
- Adjust the backtesting parameters (date range, initial capital) in `main.py`.
- Extend the `Backtester` class in `src/backtesting/backtester.py` to add more sophisticated backtesting features.

## Future Improvements
- Add more trading strategies (e.g., Bollinger Bands, MACD)
- Implement real-time trading with live data
- Add more performance metrics and visualizations
- Integrate with a cryptocurrency exchange API for live trading
- Add more advanced backtesting features (e.g., slippage, transaction costs)
- Implement a more robust and user-friendly command-line interface


## Contributing

This project is still in development. Feel free to fork the repository and submit pull requests for any improvements or bug fixes.

## License

[MIT License](https://opensource.org/licenses/MIT)