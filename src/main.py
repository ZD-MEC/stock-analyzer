import logging
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import data_processor
from api_client import fetch_stock_data
from dotenv import load_dotenv
import os



# this is the main code that is calling for function that will retreive the disired data.
# this code is the UI for the user.
# In case the user has entered wrong values or the server has issues related to connectivity or any other type of issue,
# the system will send a clear message of what went wrong

# defualt API key
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
    layout="centered"
)

st.title("Stock Analyzer")
comp_symbol = st.text_input("Please enter the stock symbol you wish to analyze: ").upper()
user_api_key = st.text_input("Enter API key or leave empty to use default")


func = st.selectbox("Please enter the function you wish to analyze.\n the choices for the analysis are:\n",
    ["TIME_SERIES_INTRADAY",
    "TIME_SERIES_DAILY",
    "TIME_SERIES_WEEKLY_ADJUSTED",
    "TIME_SERIES_MONTHLY_ADJUSTED",
    "GLOBAL_QUOTE"])



if st.button("Analyze"):
    if not user_api_key.strip():
        user_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not comp_symbol.strip():
        st.error("Please enter a valid stock symbol")
        st.session_state["analyze_clicked"] = False
        st.stop()
    # שמור קלטים ב-session_state
    st.session_state["comp_symbol"] = comp_symbol
    st.session_state["user_api_key"] = user_api_key
    st.session_state["func"] = func
    st.session_state["analyze_clicked"] = True

if st.session_state.get("analyze_clicked", False):

    comp_symbol = st.session_state.get("comp_symbol", "")
    user_api_key = st.session_state.get("user_api_key", "")
    func = st.session_state.get("func", "")

    data_j, data_df = fetch_stock_data(func, comp_symbol, user_api_key)

    if data_df is None or data_j is None or data_df.empty or (len(data_j) == 0):
        st.error("Data is empty, please try different company")
        logging.error("Data is empty")
        st.session_state["analyze_clicked"] = False
        st.stop()

    elif data_df is not None:
        st.success(f"Analyzing {comp_symbol} data")


    func_map = {
        "TIME_SERIES_INTRADAY": data_processor.analyze_intraday,
        "TIME_SERIES_DAILY": data_processor.analyze_daily,
        "TIME_SERIES_WEEKLY_ADJUSTED": data_processor.analyze_weekly_adjusted,
        "TIME_SERIES_MONTHLY_ADJUSTED": data_processor.analyze_monthly_adjusted,
        "GLOBAL_QUOTE": data_processor.analyze_quote
    }


    if func in func_map and data_df is not None:
        func_map[func](data_j, data_df)