import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging

# MAIN ROUTE FUNCTIONS
def analyze_daily(data_j, data_df):
    st.text("Analyzing daily")
    analyze_general(data_df, mode='daily')

def analyze_weekly_adjusted(data_j, data_df):
    st.text("Analyzing weekly")
    analyze_general(data_df, mode='weekly')

def analyze_monthly_adjusted(data_j, data_df):
    st.text("Analyzing monthly")
    analyze_general(data_df, mode='monthly')

# GENERAL ANALYSIS

def analyze_general(data_df, mode):

    #Receives the DataFrame and selected mode.
    #Presents checkboxes for which graphs to show,
    #handles the graphs' layout and insights button.

    # Data validity checks
    expected_columns = ['open', 'high', 'low', 'close', 'volume']
    if not all(column in data_df.columns for column in expected_columns):
        st.text("issue with expected data, try different data type")
        logging.error("Data columns is not in dataframe")
        return

    st.title(f"Compare {mode} differences and changes across time")

    # Checkbox UI for user selection of graphs (default: not shown)
    fig_1_check = st.checkbox(f"Show graph of {mode} difference between prices and parameters", value=False)
    fig_2_check = st.checkbox(f"Show graph: Compare {mode} change in % vs volume across time", value=False)
    text_fig_1 = f"This graph shows the {mode} change in open, close, max and min price through time"
    text_fig_2 = f"This graph shows the {mode} change in % of stock closing price along volume through time"

    # Prepare figures if needed
    fig_1 = plot_prices_vs_time(data_df, mode) if fig_1_check else None
    fig_2 = plot_pct_vs_volume(data_df, mode) if fig_2_check else None

    # Dynamic layout for single/double graph
    if fig_1_check and fig_2_check:
        col1, col2 = st.columns(2)
        with col1:
            if fig_1 is not None:
                st.pyplot(fig_1, use_container_width=True)
                st.caption(text_fig_1)
        with col2:
            if fig_2 is not None:
                st.pyplot(fig_2, use_container_width=True)
                st.caption(text_fig_2)
    elif fig_1_check and not fig_2_check:
        col_mid = st.columns([1, 2, 1])[1]
        with col_mid:
            if fig_1 is not None:
                st.pyplot(fig_1, use_container_width=True)
                st.caption(text_fig_1)
    elif fig_2_check and not fig_1_check:
        col_mid = st.columns([1, 2, 1])[1]
        with col_mid:
            if fig_2 is not None:
                st.pyplot(fig_2, use_container_width=True)
                st.caption(text_fig_2)

    #Insights: always shown automatically
    insights(data_df, mode)

# PLOT FUNCTIONS

def plot_prices_vs_time(data_df, mode):

    # Plots lines for open, high, low, close prices across time.
    # Returns a Matplotlib Figure.

    required_cols = ['Date', 'open', 'high', 'low', 'close']
    missing = [col for col in required_cols if col not in data_df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}. Cannot plot prices vs time.")
        return None

    # Melt dataframe to long format for seaborn
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

    # Plots % change in closing price (line) vs volume (line, secondary y-axis).
    # Returns a Matplotlib Figure.

    required_columns = ['close', 'volume', 'Date']
    missing = [col for col in required_columns if col not in data_df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}. Cannot plot change in % vs volume.")
        return None

    data_df_temp = data_df.copy()
    change_col = f"{mode} change in %"
    data_df_temp[change_col] = data_df_temp['close'].pct_change() * 100

    # Drop rows with missing data
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
    color_2_2 = '#000000'
    ax_2_2.set_ylabel('Volume', color=color_2_2)
    plot_2, = ax_2_2.plot(plot_df['Date'], plot_df['volume'], color=color_2_2, alpha=0.2, label='Volume')
    ax_2_2.tick_params(axis='y', labelcolor=color_2_2)
    plots = [plot_1, plot_2]
    labels = [i.get_label() for i in plots]

    ax_2_1.legend(plots, labels, loc='upper left')

    fig_2.tight_layout()
    ax_2_1.set_title(f'{mode.capitalize()} Percent Change vs Volume')
    return fig_2

#INSIGHTS FUNCTION

def insights(data_df, mode):

    # Shows period-based statistics with filter options:
    # Maximum/Minimum close, average volume, 7-day rolling average (if daily)
    # Volatility per period
    # Ability to filter by period or show only extreme outliers
    # Analyst commentary shown only for filtered periods

    df = data_df.copy()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    if mode == 'daily':
        period_col = 'YearMonth'
        df[period_col] = df['Date'].dt.to_period('M')
        group_desc = "month"
    elif mode == 'weekly':
        period_col = 'YearMonth'
        df[period_col] = df['Date'].dt.to_period('M')
        group_desc = "month"
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

    # Calculate volatility per period
    agg['Volatility'] = (agg['Max Close'] - agg['Min Close']) / agg['Max Close']

    # Interactive Filter Controls
    st.markdown(f"#### {group_desc.capitalize()}ly Volume & Close Price Stats ({mode.capitalize()} Data)")

    # Filter by period (select specific period or show all)
    period_options = agg[period_col].astype(str).tolist()
    period_selected = st.selectbox(f"Select {group_desc} to show", ["Show all"] + period_options)

    # Filter: Only outliers (high volatility)
    show_outliers = st.checkbox("Show only high volatility periods (Volatility > 15%)", value=False)

    filtered = agg.copy()
    if period_selected != "Show all":
        filtered = filtered[filtered[period_col].astype(str) == period_selected]
    if show_outliers:
        filtered = filtered[filtered['Volatility'] > 0.15]

    # Show the filtered DataFrame
    st.dataframe(
        filtered.style.format({
            'Max Close': '{:.2f}',
            'Min Close': '{:.2f}',
            f'Average {group_desc.capitalize()} Volume': '{:,.0f}',
            **({'7d Rolling Avg Close': '{:.2f}'} if mode == 'daily' else {}),
            'Volatility': '{:.2%}'
        })
    )

    # Analyst Commentary for Filtered Periods Only
    st.markdown(f"#### Automated Analyst Commentary for Selected Period(s)")
    volatility_threshold = 0.08
    avg_volume_all = agg[f'Average {group_desc.capitalize()} Volume'].mean()

    for idx, row in filtered.iterrows():
        max_close = row['Max Close']
        min_close = row['Min Close']
        avg_volume = row[f'Average {group_desc.capitalize()} Volume']
        volatility = row['Volatility']
        period_str = str(row[period_col])

        if volatility > volatility_threshold:
            msg = f"**{period_str}**: The stock was highly volatile ({volatility:.1%} price range). "
        elif volatility < 0.03:
            msg = f"**{period_str}**: The stock was particularly stable. "
        else:
            msg = f"**{period_str}**: Moderate price changes observed. "

        if avg_volume > avg_volume_all * 1.2:
            msg += "Trading volume was significantly above average."
        elif avg_volume < avg_volume_all * 0.8:
            msg += "Trading volume was unusually low."
        else:
            msg += "Trading volume was typical."

        st.info(msg)
