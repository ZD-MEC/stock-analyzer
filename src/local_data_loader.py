import pandas as pd
import json


def load_local_json(filepath, func, symbol="IBM"):
    """
    Loads local Alpha Vantage JSON (as saved from API),
    processes it like fetch_stock_data, returns (data_j, data_df)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data_j = json.load(f)

    # Define the mapping as ב־api_client
    map_keys = {
        "TIME_SERIES_INTRADAY": "Time Series (5min)",
        "TIME_SERIES_DAILY": "Time Series (Daily)",
        "TIME_SERIES_WEEKLY_ADJUSTED": "Weekly Adjusted Time Series",
        "TIME_SERIES_MONTHLY_ADJUSTED": "Monthly Adjusted Time Series"
    }
    mapped_key = map_keys.get(func)
    if mapped_key not in data_j:
        return data_j, None

    raw_data = data_j[mapped_key]
    data_df = pd.DataFrame.from_dict(raw_data, orient="index")
    data_df.columns = data_df.columns.str.strip().str.lower()

    rename_map = {
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close',
        '5. volume': 'volume',
        '6. volume': 'volume',
        '7. dividend amount': 'dividend_amount',
        '8. split coefficient': 'split_coefficient'
    }
    data_df.rename(columns=rename_map, inplace=True)

    keep_cols = [c for c in ['open', 'high', 'low', 'close', 'volume',
                             'dividend_amount', 'split_coefficient'] if c in data_df.columns]
    data_df = data_df[keep_cols]

    for col in keep_cols:
        data_df[col] = pd.to_numeric(data_df[col], errors='coerce')

    data_df.reset_index(inplace=True)
    data_df.rename(columns={'index': 'Date'}, inplace=True)
    data_df['Date'] = pd.to_datetime(data_df['Date'], errors='coerce')
    data_df = data_df.sort_values(by='Date')

    data_df['symbol'] = symbol
    return data_j, data_df
