import ccxt

class ExchangeDataCollector:
    def __init__(self, exchange_name='coinbase'):
        self.exchange = getattr(ccxt, exchange_name)()

    def fetch_ohlcv(self, symbol, timeframe='1m'):
        return self.exchange.fetch_ohlcv(symbol, timeframe)

# Usage
def main():
    collector = ExchangeDataCollector()
    data = collector.fetch_ohlcv('BTC/USD')
    print(data)

if __name__ == '__main__':
    main()