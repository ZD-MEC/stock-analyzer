
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
    analyze_timeseries(data_df, mode='intraday')



def analyze_daily (data_j, data_df):
    st.text("Analyzing daily")
    analyze_timeseries(data_df, mode='daily')



def analyze_weekly_adjusted (data_j, data_df):
    st.text("Analyzing weekly")
    analyze_timeseries(data_df, mode='weekly')



def analyze_monthly_adjusted (data_j, data_df):
    st.text("Analyzing monthly")
    analyze_timeseries(data_df, mode='monthly')


def analyze_quote (data_j, data_df):
    st.text("Analyzing quote")
    analyze_timeseries(data_df, mode='quote')


#need to make sure I add the mode to the function
def analyze_timeseries(data_df, mode):
    st.write(data_df.head())
    st.write(data_df.dtypes)
    #building the data table in a such a way that it would fit the desired structure for seaburn methods.
    # also checking errors in columns names
    expected_columns = ['open', 'high', 'low', 'close', 'volume']
    error_flag = False
    if not all(column in data_df.columns for column in expected_columns):
        st.text("issue with expected data, try different data type")
        logging.error("Data columns is not in dataframe")
        error_flag = True

    st.title(f"Compare {mode} differences and changes across time" )
    fig_1_check = st.checkbox(f"show graph of {mode} difference between prices and parameters")
    fig_2_check = st.checkbox(f"show graph Compare {mode} change in % vs volume across time")

    col1, col2 = st.columns(2)
    text_fig_1 = f"This graph shows the {mode} change in open, close, max and min price through time"
    text_fig_2 = f"This graph shows the {mode} change in % of stock closing price along volume through time"

    # user will receive a checkbox for graph view with insights
    #if other graph will be added in the future - need to write a if loop for that
    if not error_flag:
        col_mid = st.columns([1, 2, 1])[1]
        fig_1 = plot_prices_vs_time(data_df, mode)
        fig_2 = plot_pct_vs_volume(data_df, mode)

        if fig_1_check and fig_2_check:
            with col1:
                if fig_1 is not None:
                    st.pyplot(fig_1)
                    st.text(text_fig_1)

            with col2:
                if fig_2 is not None:
                    st.pyplot(fig_2)
                    st.text(text_fig_2)

        elif fig_1_check and not fig_2_check:
            with col_mid:
                if fig_1 is not None:
                    st.pyplot(fig_1)
                    st.text(text_fig_1)


        elif fig_2_check and not fig_1_check:
            with col_mid:
                if fig_2 is not None:
                    st.pyplot(fig_2)
                    st.text(text_fig_2)


    # writing insights for user on the data showed in graph


def plot_prices_vs_time (data_df,mode):
    # Check necessary columns
    required_cols = ['Date', 'open', 'high', 'low', 'close']
    missing = [col for col in required_cols if col not in data_df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}. Cannot plot prices vs time.")
        return None
        # building graph that will contain several lines, each representing different data
    df_long = pd.melt(data_df, id_vars=['Date'], value_vars=['open', 'high', 'low', 'close'],
                          var_name='Price_type', value_name='Value')

    if df_long.empty or df_long['Value'].isnull().all():
        st.error("Not enough valid data to plot prices vs time.")
        return None

    fig_1, ax_1 = plt.subplots(figsize=(18, 8))
    sns.lineplot(data=df_long, x='Date', y='Value', hue='Price_type', ax=ax_1)
    ax_1.set_xlabel('Date')
    ax_1.set_ylabel('Value')
    ax_1.legend(loc='upper left')
    ax_1.grid(True)
    symbol = data_df['symbol'].iloc[0] if 'symbol' in data_df.columns else "Selected Stock"
    ax_1.set_title(f"{symbol} {mode} Price")
    return fig_1

def plot_pct_vs_volume(data_df, mode):
    required_columns = ['close', 'volume', 'Date']
    missing = [col for col in required_columns if col not in data_df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}. Cannot plot change in % vs volume.")
        return None

    data_df_temp = data_df.copy()
    change_col = f"{mode} change in %"
    data_df_temp[change_col] = data_df_temp['close'].pct_change() * 100

    # Drop rows with missing data (date, close, volume)
    plot_df = data_df_temp.dropna(subset=['Date', 'close', 'volume', change_col])

    if plot_df.empty or plot_df[change_col].isnull().all():
        st.error("Not enough data to plot change in % vs volume. Please select different stock or function.")
        return None

    fig_2, ax_2_1 = plt.subplots(figsize=(18, 8))
    color_2_1 = 'tab:blue'
    ax_2_1.set_xlabel('Date')
    ax_2_1.set_ylabel(change_col, color=color_2_1)
    plot_1, = ax_2_1.plot(plot_df['Date'], plot_df[change_col], color=color_2_1, label='Daily Change in %')
    ax_2_1.tick_params(axis='y', labelcolor=color_2_1)

    ax_2_2 = ax_2_1.twinx()
    color_2_2 = 'tab:red'
    ax_2_2.set_ylabel('Volume', color=color_2_2)
    plot_2, = ax_2_2.plot(plot_df['Date'], plot_df['volume'], color=color_2_2, alpha=0.2, label='Volume')
    ax_2_2.tick_params(axis='y', labelcolor=color_2_2)
    plots = [plot_1, plot_2]
    labels = [i.get_label() for i in plots]

    ax_2_1.legend(plots, labels, loc='upper left')

    fig_2.tight_layout()
    ax_2_1.set_title(f'{mode} Percent Change vs Volume')
    return fig_2




