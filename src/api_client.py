import logging
import streamlit as st
import pandas as pd
import requests


def fetch_stock_data(func, comp, api_key):
    url = "https://www.alphavantage.co/query"
    parameters = {
        "function": func,
        "symbol": comp,
        "apikey": api_key
    }

    try:
        response = requests.get(url, params=parameters)
        response.raise_for_status()
        data_j = response.json()

    except requests.exceptions.RequestException as e:
        msg = "Unexpected error occurred while fetching data."
        st.error(msg)
        logging.error(msg, exc_info=True)
        return None, None

    try:
        map_keys = {
            "TIME_SERIES_INTRADAY": "Time Series (5min)",
            "TIME_SERIES_DAILY": "Time Series (Daily)",
            "TIME_SERIES_WEEKLY": "Weekly Time Series",
            "TIME_SERIES_WEEKLY_ADJUSTED": "Weekly Adjusted Time Series",
            "TIME_SERIES_MONTHLY": "Monthly Time Series",
            "TIME_SERIES_MONTHLY_ADJUSTED": "Monthly Adjusted Time Series"
        }

        mapped_key = map_keys.get(func)
        if mapped_key not in data_j:
            msg = f"Expected key '{mapped_key}' not found in API response."
            st.error(msg)
            logging.error(msg)
            return None, None

        raw_data = data_j[mapped_key]
        data_df = pd.DataFrame.from_dict(raw_data, orient="index")

        # Normalize and clean column names first
        data_df.columns = data_df.columns.str.strip().str.lower()

        # Expected mapping after cleaning
        rename_map = {
            '1. open': 'open',
            '2. high': 'high',
            '3. low': 'low',
            '4. close': 'close',
            '5. volume': 'volume'
        }

        data_df.rename(columns=rename_map, inplace=True)

        # Check again if all expected columns exist
        expected_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data_df.columns for col in expected_cols):
            msg = f"Missing columns after rename: {data_df.columns.tolist()}"
            st.error("Missing one or more expected columns in data.")
            logging.error(msg)
            return None, None

        # Convert columns to numeric
        for col in expected_cols:
            data_df[col] = pd.to_numeric(data_df[col], errors='coerce')

        # Fix the date column
        data_df.reset_index(inplace=True)
        data_df.rename(columns={'index': 'Date'}, inplace=True)
        data_df['Date'] = pd.to_datetime(data_df['Date'], errors='coerce')
        data_df = data_df.sort_values(by='Date')

        data_df['symbol'] = comp.upper()
        return data_j, data_df

    except Exception as e:
        msg = "Failed to process data structure from API response."
        st.error(msg)
        logging.error(msg, exc_info=True)
        return None, None
