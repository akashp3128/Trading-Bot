import json
import os
import pandas as pd
from pymongo import MongoClient

class Database:
    def __init__(self, file_path='data.json'):
        self.file_path = file_path
        self.data = self.load_data()

        # MongoDB setup
        self.mongo_client = MongoClient("mongodb://localhost:27017/")
        self.mongo_db = self.mongo_client["crypto_trading_bot"]

    def load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save_data()

    # MongoDB methods
    def insert_historical_data(self, symbol, data):
        collection = self.mongo_db[f"{symbol}_historical_data"]
        collection.insert_many(data.to_dict('records'))

    def get_historical_data(self, symbol, start_date, end_date):
        collection = self.mongo_db[f"{symbol}_historical_data"]
        data = collection.find({
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        })
        return pd.DataFrame(list(data))

    def insert_backtest_results(self, strategy_name, results):
        collection = self.mongo_db["backtest_results"]
        collection.insert_one({
            "strategy": strategy_name,
            "results": results.to_dict('records')
        })

    def get_backtest_results(self, strategy_name):
        collection = self.mongo_db["backtest_results"]
        return collection.find_one({"strategy": strategy_name})

    def close(self):
        self.mongo_client.close()