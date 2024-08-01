from src.data_collection.exchange_data import ExchangeDataCollector
from src.utils.database import Database
from src.data_processing.processor import process_ohlcv
from src.strategy.simple_moving_average import sma_crossover_strategy

def main():
    collector = ExchangeDataCollector()
    db = Database()

    try:
        # Collect data
        data = collector.fetch_ohlcv('BTC/USD')
        
        print("Raw OHLCV data:")
        print(data[:5])  # Print the first 5 entries

        # Store raw data
        db.insert_ohlcv('BTC_USD', data)

        # Read stored data
        stored_data = db.read_ohlcv('BTC_USD')
        print("\nStored data:")
        print(stored_data[:5])

        # Process data
        processed_data = process_ohlcv(stored_data)

        # Apply strategy
        df_with_signals = sma_crossover_strategy(processed_data)

        print("\nProcessed data with signals:")
        print(df_with_signals.tail())

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()