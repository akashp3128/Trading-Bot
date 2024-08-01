# Crypto Trading Bot

This project is a cryptocurrency trading bot that fetches OHLCV (Open, High, Low, Close, Volume) data from Coinbase, processes it, and applies a simple moving average (SMA) crossover strategy to generate trading signals.

## Current Features

- Fetch real-time OHLCV data from Coinbase for BTC/USD
- Store and retrieve data using a local JSON file
- Process OHLCV data and calculate moving averages
- Generate trading signals based on SMA crossover strategy

## Project Structure
crypto_trading_bot/
├── src/
│   ├── data_collection/
│   │   └── exchange_data.py
│   ├── data_processing/
│   │   └── processor.py
│   ├── strategy/
│   │   └── simple_moving_average.py
│   └── utils/
│       └── database.py
├── main.py
├── requirements.txt
└── README.md

## Setup and Installation

1. Clone this repository:

2. Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate

3. Install the required packages:
pip install -r requirements.txt

## Usage

Run the main script:
python main.py

This will fetch the latest BTC/USD data from Coinbase, process it, and print the results including the generated trading signals.

## Future Improvements

- Implement backtesting functionality
- Add more sophisticated trading strategies
- Create a simulated trading environment
- Implement real-time data streaming and trading
- Add data visualization

## Contributing

This project is still in development. Feel free to fork the repository and submit pull requests for any improvements or bug fixes.

## License

[MIT License](https://opensource.org/licenses/MIT)