import pandas as pd
import requests
from datetime import datetime
from ..utils.database import Database

def get_historical_data(symbol, start_date, end_date):
    print(f"Fetching data for {symbol} from {start_date} to {end_date}")
    
    db = Database()
    data = db.get_historical_data(symbol, start_date, end_date)
    
    if data.empty:
        # If data is not in MongoDB, fetch it from the API
        url = f"https://api.pro.coinbase.com/products/{symbol}/candles"
        params = {
            'start': start_date,
            'end': end_date,
            'granularity': 86400  # daily candles
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error response from API: {response.text}")
            return pd.DataFrame()
        
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'low', 'high', 'open', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        
        # Store the fetched data in MongoDB
        db.insert_historical_data(symbol, df)
    else:
        df = data
        df.set_index('timestamp', inplace=True)
    
    db.close()
    return df