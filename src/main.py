import struct
import logging
from ast import literal_eval

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

import data_processor
from api_client import fetch_stock_data
from data_processor import *
from dotenv import load_dotenv
import os



# this is the main code that is calling for function that will retreive the disired data.
# this code is the UI for the user.
# In case the user has entered wrong values or the server has issues related to connectivity or any other type of issue,
# the system will send a clear message of what went wrong


       # func_type = next((f for f in data if "Time Series" in f), None)
       # if func_type is None:
        #    st.error("Please enter a valid ")
        # df = pd.DataFrame(data[func_type])

# loding API key
load_dotenv()

#Config the logger
logging.basicConfig(
    filename='app.log',
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Creating the UI
st.set_page_config(
    page_title="Stock Analyzer",
    page_icon="🧊",
    layout="centered"
)

comp_symbol = st.text_input("Please enter the stock symbol you wish to analyze: ").upper()
user_api_key = st.text_input("Enter API key or leave empty to use default")


func = st.selectbox("Please enter the function you wish to analyze.\n the choices for the analysis are:\n", ["TIME_SERIES_INTRADAY",
    "TIME_SERIES_DAILY",
    "TIME_SERIES_WEEKLY",
    "TIME_SERIES_WEEKLY_ADJUSTED",
    "TIME_SERIES_MONTHLY",
    "TIME_SERIES_MONTHLY_ADJUSTED",
    "GLOBAL_QUOTE"])



if st.button("Analyze"):

    try:
        if not user_api_key.strip():
          #  user_api_key = user_api_key if user_api_key else os.getenv("ALPHA_VANTAGE_API_KEY")
            user_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
         #   st.text(f"[Default API key loaded from .env: {user_api_key}]")
      #      st.error("Please enter a valid API key or leave empty to use default API key")

    except Exception as e:
        st.error("Unexpected error, Try again later")
        logging.error(str(e), exc_info=True)
        st.stop()

    try:
        if not comp_symbol.strip():
            st.error("Please enter a valid stock symbol")

    except Exception as e:
        st.error("Company symbol not found, Try symbols like AAPL or AMZN or INTC or IBM")
        logging.error(str(e), exc_info=True)
        st.stop()

    data_j, data_df = fetch_stock_data(func, comp_symbol, user_api_key)

    if data_df is None or data_j is None or data_df.empty or (len(data_j) == 0):
        st.error("Data is empty, please try different company")
        logging.error("Data is empty")
        st.stop()

    elif data_df is not None:
        st.success(f"Analyzing {comp_symbol} data")


    func_map = {
        "TIME_SERIES_INTRADAY": data_processor.analyze_intraday,
        "TIME_SERIES_DAILY": data_processor.analyze_daily,
        "TIME_SERIES_WEEKLY": data_processor.analyze_weekly,
        "TIME_SERIES_WEEKLY_ADJUSTED": data_processor.analyze_weekly_adjusted,
        "TIME_SERIES_MONTHLY": data_processor.analyze_monthly,
        "TIME_SERIES_MONTHLY_ADJUSTED": data_processor.analyze_monthly_adjusted,
        "GLOBAL_QUOTE": data_processor.analyze_quote
    }

    if func in func_map and data_df is not None:
        func_map[func](data_j, data_df)
        st.stop()








#st.title("ניתוח מניות וקריפטו")
#symbol = st.text_input("הכנס סמל מניה (למשל AAPL)")
#if st.button("נתח מניה"):
#    st.write(f"המשתמש ביקש לנתח את: {symbol}")

