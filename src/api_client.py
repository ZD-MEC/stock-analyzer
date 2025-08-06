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
        st.text(data_j)

    except requests.exceptions.RequestException:
        msg = "Unexpected error occurred while fetching data."
        st.error(msg)
        logging.error(msg, exc_info=True)
        return None, None

    try:
        map_keys = {
            "TIME_SERIES_INTRADAY": "Time Series (5min)",
            "TIME_SERIES_DAILY": "Time Series (Daily)",
            "TIME_SERIES_WEEKLY_ADJUSTED": "Weekly Adjusted Time Series",
            "TIME_SERIES_MONTHLY_ADJUSTED": "Monthly Adjusted Time Series"
        }

        mapped_key = map_keys.get(func)
        if mapped_key not in data_j:
            msg_key = f"Expected key '{mapped_key}' not found in API response."
            st.error(msg_key)
            logging.error(msg_key)
            return None, None

        raw_data = data_j[mapped_key]
        data_df = pd.DataFrame.from_dict(raw_data, orient="index")

        # Normalize and clean column names first
        data_df.columns = data_df.columns.str.strip().str.lower()

        # Build a mapping from the API's column names to standard names
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

        # Keep only relevant columns (this also ensures any 'adjusted' column is kept if exists)
        keep_cols = [c for c in ['open', 'high', 'low', 'close', 'volume',
                                 'dividend_amount', 'split_coefficient'] if c in data_df.columns]
        # Check if all expected columns exist
        if not all(col in data_df.columns for col in keep_cols):
            msg = f"Missing columns after rename: {data_df.columns.tolist()}"
            st.error("Missing one or more expected columns in data.")
            logging.error(msg)
            return None, None
        data_df = data_df[keep_cols]

        # Convert columns to numeric
        for col in keep_cols:
            data_df[col] = pd.to_numeric(data_df[col], errors='coerce')

        # Fix the date column
        data_df.reset_index(inplace=True)
        data_df.rename(columns={'index': 'Date'}, inplace=True)
        data_df['Date'] = pd.to_datetime(data_df['Date'], errors='coerce')
        data_df = data_df.sort_values(by='Date')

        data_df['symbol'] = comp.upper()
        return data_j, data_df

    except Exception:
        msg = "Failed to process data structure from API response."
        st.error(msg)
        logging.error(msg, exc_info=True)
        return None, None
