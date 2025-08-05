from dbm.sqlite3 import error

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import logging

from streamlit import columns, checkbox


#This file contains functions that does the analysis of the data according to selected option,
# and according to how the API dictionary contains the data.

def analyze_intraday (data_j, data_df):
    st.text("Analyzing Intraday")
    pass


def analyze_daily (data_j, data_df):
    #st.write(data_df.head())
    #st.write(data_df.dtypes)
    #building the data table in a such a way that it would fit the desired structure for seaburn methods.
    # also checking errors in columns names
    expected_columns = ['open', 'high', 'low', 'close', 'volume']
    error_flag = False
    if not all(column in data_df.columns for column in expected_columns):
        st.text("issue with expected data, try different data type")
        logging.error("Data columns is not in dataframe")
        error_flag = True

    st.title("Compare daily differences and changes across time", )
    fig_1_check = st.checkbox("show graph of daily difference between prices and parameters")
    fig_2_check = st.checkbox("show graph Compare daily change in % vs volume across time")

    col1, col2 = st.columns(2)
    text_fig_1 = "This graph shows the daily change in open, close, max and min price through time"
    text_fig_2 = "This graph shows the daily change in % of stock closing price along volume through time"

    # user will receive a checkbox for graph view with insights
    #if other graph will be added in the future - need to write a if loop for that
    if not error_flag:
        col_mid = st.columns([1, 2, 1])[1]
        fig_1 = plot_prices_vs_time(data_df)
        fig_2 = plot_pct_vs_volume(data_df)
        if fig_1_check and fig_2_check:
            with col1:
                st.pyplot(fig_1)
                st.text(text_fig_1)
            with col2:
                st.pyplot(fig_2)
                st.text(text_fig_2)

        elif fig_1_check and not fig_2_check:
            with col_mid:
                st.pyplot(fig_1)
                st.text(text_fig_1)

        elif fig_2_check and not fig_1_check:
            with col_mid:
                st.pyplot(fig_2)
                st.text(text_fig_2)


    # writing insights for user on the data showed in graph


def plot_prices_vs_time (data_df):
        # building graph that will contain several lines, each representing different data
    df_long = pd.melt(data_df, id_vars=['Date'], value_vars=['open', 'high', 'low', 'close'],
                          var_name='Price_type', value_name='Value')
    fig_1, ax_1 = plt.subplots()
    sns.lineplot(data=df_long, x='Date', y='Value', hue='Price_type', ax=ax_1)
    ax_1.set_xlabel('Date')
    ax_1.set_ylabel('Value')
    ax_1.legend(loc='upper left')
    ax_1.grid(True)
    symbol = data_df['symbol'].iloc[0] if 'symbol' in data_df.columns else "Selected Stock"
    ax_1.set_title(f"{symbol} Daily Price")
    return fig_1

def plot_pct_vs_volume(data_df):
    data_df_temp = data_df.copy()
    data_df_temp['daily change in %'] = data_df_temp['close'].pct_change() * 100
    fig_2, ax_2_1 = plt.subplots()
    color_2_1 = 'tab:blue'
    ax_2_1.set_xlabel('Date')
    ax_2_1.set_ylabel('Daily Change in %', color=color_2_1)
    plot_1, = ax_2_1.plot(data_df_temp['Date'], data_df_temp['daily change in %'], color=color_2_1, label='Daily Change in %')
    ax_2_1.tick_params(axis='y', labelcolor=color_2_1)

    ax_2_2 = ax_2_1.twinx()
    color_2_2 = 'tab:red'
    ax_2_2.set_ylabel('Volume', color=color_2_2)
    plot_2, = ax_2_2.plot(data_df_temp['Date'], data_df_temp['volume'], color=color_2_2, alpha=0.2, label='Volume')
    ax_2_2.tick_params(axis='y', labelcolor=color_2_2)
    plots = [plot_1, plot_2]
    labels = [i.get_label() for i in plots]

    ax_2_1.legend(plots, labels, loc='upper left')

    fig_2.tight_layout()
    ax_2_1.set_title('Daily Percent Change vs Volume')
    return fig_2

    """"
    df_long = pd.melt(data_df, id_vars=['Date'], value_vars=['daily change in %', 'volume'],
                      var_name='Price_type', value_name='Value')
    fig_2, ax_2 = plt.subplots()
    sns.lineplot(data=df_long, x='Date', y='Value', hue='Price_type', ax=ax_2)
    ax_2.set_xlabel('Date')
    ax_2.set_ylabel('Value')
    ax_2.legend(loc='upper left')
    ax_2.grid(True)
    symbol = data_df['symbol'].iloc[0] if 'symbol' in data_df.columns else "Selected Stock"
    ax_2.set_title(f"{symbol} Daily Price changes in % vs Volume")
    st.pyplot(fig_2)
"""







def analyze_weekly (data_j, data_df):
    pass


def analyze_weekly_adjusted (data_j, data_df):
    pass


def analyze_monthly (data_j, data_df):
    pass


def analyze_monthly_adjusted (data_j, data_df):
    pass


def analyze_quote (data_j, data_df):
    pass