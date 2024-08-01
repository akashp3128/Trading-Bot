import json
from datetime import datetime

class Database:
    def __init__(self, file_path='data.json'):
        self.file_path = file_path

    def insert_ohlcv(self, symbol, data):
        formatted_data = []
        for entry in data:
            formatted_entry = {
                'timestamp': entry[0],
                'open': entry[1],
                'high': entry[2],
                'low': entry[3],
                'close': entry[4],
                'volume': entry[5]
            }
            formatted_data.append(formatted_entry)
        
        with open(self.file_path, 'w') as f:
            json.dump({symbol: formatted_data}, f)

    def read_ohlcv(self, symbol):
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            return data.get(symbol, [])
        except FileNotFoundError:
            return []

# Usage
# db = Database()
# db.insert_ohlcv('BTC_USD', data)