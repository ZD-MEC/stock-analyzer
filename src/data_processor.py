
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
    analyze_general(data_df, mode='intraday')

def analyze_daily (data_j, data_df):
    st.text("Analyzing daily")
    analyze_general(data_df, mode='daily')

def analyze_weekly_adjusted (data_j, data_df):
    st.text("Analyzing weekly")
    analyze_general(data_df, mode='weekly')

def analyze_monthly_adjusted (data_j, data_df):
    st.text("Analyzing monthly")
    analyze_general(data_df, mode='monthly')

def analyze_quote (data_j, data_df):
    st.text("Analyzing quote")
    analyze_general(data_df, mode='quote')

#need to make sure I add the mode to the function
def analyze_general(data_df, mode):
    #st.write(data_df.head())
    #st.write(data_df.dtypes)
    #building the data table in such a way that it would fit the desired structure for seaburn methods.
    # also checking errors in columns names
    expected_columns = ['open', 'high', 'low', 'close', 'volume']
    error_flag = False
    if not all(column in data_df.columns for column in expected_columns):
        st.text("issue with expected data, try different data type")
        logging.error("Data columns is not in dataframe")
        return

    st.title(f"Compare {mode} differences and changes across time" )
    fig_1_check = st.checkbox(f"show graph of {mode} difference between prices and parameters")
    fig_2_check = st.checkbox(f"show graph Compare {mode} change in % vs volume across time")

    col1, col2 = st.columns(2)
    text_fig_1 = f"This graph shows the {mode} change in open, close, max and min price through time"
    text_fig_2 = f"This graph shows the {mode} change in % of stock closing price along volume through time"

    # user will receive a checkbox for graph view with insights
    #if other graph will be added in the future - need to write a if loop for that
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

    # --- Insights below the graphs ---
    # Combine explanations depending on which graphs are shown (no duplicates)
    main_insights = []
    if fig_1_check:
        main_insights.append(text_fig_1)
    if fig_2_check:
        if text_fig_2 not in main_insights:
            main_insights.append(text_fig_2)
    if main_insights:
        st.markdown("**Key takeaways from the selected graph(s):**")
        for text in main_insights:
            st.markdown(f"- {text}")

    # Separate insights section (only when the user clicks the button)
    show_insights_button = st.button("Show insights for this data")
    if show_insights_button:
        insights(data_df, mode)


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
    ax_2_1.set_title(f'{mode.capitalize()} Percent Change vs Volume')
    return fig_2


def insights(data_df, mode):
    """
    Show period-based statistics: max/min close, average volume,
    and 7-day rolling average (if daily), grouped by period (month/week/year)
    :param data_df: Clean dataframe with 'Date', 'close', 'volume'
    :param mode: one of 'daily', 'weekly', 'monthly'
    """
    df = data_df.copy()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    # Set period column and aggregation rules by mode
    if mode == 'daily':
        period_col = 'YearMonth'
        df[period_col] = df['Date'].dt.to_period('M')
        group_desc = "month"
    elif mode == 'weekly':
        period_col = 'YearWeek'
        df[period_col] = df['Date'].dt.strftime('%Y-%U')
        group_desc = "week"
    elif mode == 'monthly':
        period_col = 'Year'
        df[period_col] = df['Date'].dt.year
        group_desc = "year"
    else:
        st.write("Unsupported mode for insights.")
        return

    # Aggregation per period
    agg = df.groupby(period_col).agg({
        'close': ['max', 'min'],
        'volume': 'mean'
    }).reset_index()
    agg.columns = [period_col, 'Max Close', 'Min Close', f'Average {group_desc.capitalize()} Volume']

    # 7-day rolling average only if daily
    if mode == 'daily':
        df['7d Rolling Avg Close'] = df['close'].rolling(window=7).mean()
        rolling = df.groupby(period_col)['7d Rolling Avg Close'].mean().reset_index()
        agg = pd.merge(agg, rolling, on=period_col, how='left')

    # Explanation text
    st.markdown(f"#### {group_desc.capitalize()}ly Volume & Close Price Stats ({mode.capitalize()} Data)")
    st.write(f"""
    - **Max Close:** Highest closing price for the {group_desc}
    - **Min Close:** Lowest closing price for the {group_desc}
    - **Average {group_desc.capitalize()} Volume:** Mean trading volume per {group_desc}
    """)
    if mode == 'daily':
        st.write("- **7d Rolling Avg Close:** Mean of the 7-day moving average closing price in the month")
    st.dataframe(agg.style.format({
        'Max Close': '{:.2f}',
        'Min Close': '{:.2f}',
        f'Average {group_desc.capitalize()} Volume': '{:,.0f}',
        **({'7d Rolling Avg Close': '{:.2f}'} if mode == 'daily' else {})
    }))


    #need to check logic
    st.markdown("#### Automated Analyst Commentary per Period")
    volatility_threshold = 0.08  # 8% תנודתיות = חודש תנודתי
    avg_volume_all = agg[f'Average {group_desc.capitalize()} Volume'].mean()

    for idx, row in agg.iterrows():
        max_close, min_close = row['Max Close'], row['Min Close']
        avg_volume = row[f'Average {group_desc.capitalize()} Volume']
        volatility = (max_close - min_close) / max_close if max_close else 0
        period_str = str(row[period_col])

        # pickness
        if volatility > volatility_threshold:
            msg = f"**{period_str}**: The stock was highly volatile ({volatility:.1%} price range). "
        elif volatility < 0.03:
            msg = f"**{period_str}**: The stock was particularly stable. "
        else:
            msg = f"**{period_str}**: Moderate price changes observed. "

        #volume size
        if avg_volume > avg_volume_all * 1.2:
            msg += "Trading volume was significantly above average."
        elif avg_volume < avg_volume_all * 0.8:
            msg += "Trading volume was unusually low."
        else:
            msg += "Trading volume was typical."

        st.info(msg)





