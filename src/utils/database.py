import pymongo
import pandas as pd
from pymongo import MongoClient

class Database:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['crypto_trading']

    def insert_historical_data(self, symbol, data):
        collection = self.db['historical_data']
        records = data.reset_index().to_dict('records')
        collection.insert_many(records)

    def get_historical_data(self, symbol, start_date, end_date):
        collection = self.db['historical_data']
        query = {
            'timestamp': {
                '$gte': pd.Timestamp(start_date),
                '$lte': pd.Timestamp(end_date)
            }
        }
        data = list(collection.find(query))
        return pd.DataFrame(data)

    def insert_backtest_results(self, strategy_name, results):
        collection = self.db['backtest_results']
        document = {
            'strategy': strategy_name,
            'results': results.to_dict('records')
        }
        collection.insert_one(document)

    def get_backtest_results(self, strategy_name):
        collection = self.db['backtest_results']
        return collection.find_one({'strategy': strategy_name})

    def close(self):
        self.client.close()