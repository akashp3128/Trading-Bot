import pandas as pd
import requests
from datetime import datetime, timedelta

def get_historical_data(symbol, start_date, end_date):
    print(f"Fetching data for {symbol} from {start_date} to {end_date}")
    url = f"https://api.pro.coinbase.com/products/{symbol}/candles"
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    all_data = []
    current_start = start
    
    while current_start < end:
        current_end = min(current_start + timedelta(days=200), end)
        
        params = {
            'start': current_start.isoformat(),
            'end': current_end.isoformat(),
            'granularity': 86400  # daily candles
        }
        
        response = requests.get(url, params=params)
        print(f"API Response status code for {current_start.date()} to {current_end.date()}: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response from API: {response.text}")
            return pd.DataFrame()
        
        data = response.json()
        
        if not isinstance(data, list):
            print(f"Unexpected data format. Received: {data}")
            return pd.DataFrame()
        
        all_data.extend(data)
        current_start = current_end + timedelta(days=1)
    
    print(f"Received {len(all_data)} total data points")
    
    if not all_data:
        print("No data received from API")
        return pd.DataFrame()

    df = pd.DataFrame(all_data, columns=['timestamp', 'low', 'high', 'open', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
    
    print(f"Processed DataFrame shape: {df.shape}")
    print(f"Processed DataFrame head:\n{df.head()}")
    
    return df