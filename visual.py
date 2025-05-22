import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# -------------------------------
# Streamlit Configuration
# -------------------------------
st.set_page_config(page_title="Stock Analysis Dashboard", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
            color: #000000;
        }
        .css-1aumxhk, .css-16huue1 {
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }
        .css-1d391kg {
            color: #d63384;
        }
        div.block-container {
            padding-top: 2rem;
        }
        img {
            display: block;
            margin: auto;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Database Connection
# -------------------------------
engine = create_engine("mysql+pymysql://root:root@127.0.0.1:3306/stocks_analysis")

# -------------------------------
# Sidebar Navigation
# -------------------------------
st.sidebar.title("📌 Navigation")
selection = st.sidebar.radio("Go to", [
    "Home",
    "Volatility Analysis",
    "Cumulative Returns",
    "Sector Performance",
    "Stock Correlation",
    "Gainers & Losers"
])

# -------------------------------
# Page Functions
# -------------------------------
def home():
    st.title("📊 Stock Analysis Dashboard")
    st.markdown("""
        Welcome to your interactive dashboard to:
        - Analyze stock trends 📈  
        - Discover top performers  
        - Explore volatility & correlation  
        - Compare sector-wise returns
    """)

def volatility_analysis():
    st.header("🔄 Top 10 Most Volatile Stocks")
    query = "SELECT * FROM volatility_analysis ORDER BY volatility DESC LIMIT 10"
    df = pd.read_sql(query, engine)

    if df.empty:
        st.warning("⚠️ No data found for volatility analysis.")
        return

    expected_columns = {"Ticker", "Volatility"}
    if not expected_columns.issubset(df.columns):
        st.error(f"❌ Expected columns not found: {expected_columns - set(df.columns)}")
        st.dataframe(df)
        return

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("📌 Most Volatile", df.iloc[0]["Ticker"], f'{df.iloc[0]["Volatility"]:.2f}')
        st.dataframe(df)
    with col2:
        fig = px.bar(   
            df,
            x='Ticker',
            y='Volatility',
            color='Volatility',
            text='Volatility',
            title="Top 10 Volatile Stocks",
            template='plotly_dark',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)


def top_5_cumulative_return():
    st.header("📈 Top 5 Cumulative Returns Over Time")
    query = "SELECT * FROM top_5_cumulative_return"
    df = pd.read_sql(query, engine)

    required_cols = {'date', 'Ticker', 'cumulative_return'}   
    missing_cols = required_cols - set(df.columns)

    if missing_cols:
        st.error(f"❌ Missing columns in database table: {', '.join(missing_cols)}")
        return

    df['date'] = pd.to_datetime(df['date'])

    final_returns = df.groupby('Ticker')['cumulative_return'].last().reset_index()
    top5_symbols = final_returns.sort_values(by='cumulative_return', ascending=False).head(5)['Ticker']
    top5_df = df[df['Ticker'].isin(top5_symbols)]

    fig = px.line(
        top5_df,
        x='date',
        y='cumulative_return',
        color='Ticker',
        title="Top 5 Stocks by Cumulative Return",
        template='plotly'
    )
    st.plotly_chart(fig, use_container_width=True)


def sectorwise_performance():
    st.title("📈 Sector Performance Dashboard")
    df=pd.read_csv("D:\project-2\sector_average_yearly_returns.csv")
    st.dataframe(df)

    # Plotly Bar Chart
    fig = px.bar(df, x="Sector", y="Average_Yearly_Return", color="Average_Yearly_Return", title="Sector Performance")

    # fig = px.bar(df, x="sector", y="Average_Yearly_Return", color="Average_Yearly_Return", title="Sector Performance")

    # Seaborn Bar Chart
    plt.figure(figsize=(15, 4))
    sns.barplot(x="Sector", y="Average_Yearly_Return", data=df, palette="Blues")
    plt.xticks(rotation=90) 
    plt.title("Average Yearly Return by Sector")
    plt.xlabel("Sector")
    plt.ylabel("Average_Yearly_Return")
    plt.grid(axis="y")
    st.pyplot(plt)
    # st.header("🏭 Sector-wise Average Yearly Return")

    # # Load first 5 rows to detect columns
    # df_sample = pd.read_sql("SELECT * FROM sectorwise_performance LIMIT 5", engine)

    # st.write("Detected columns in sectorwise_performance table:", list(df_sample.columns))

    # # Try to identify start and end price columns heuristically
    # start_candidates = [col for col in df_sample.columns if 'start' in col.lower() or 'open' in col.lower()]
    # end_candidates = [col for col in df_sample.columns if 'end' in col.lower() or 'close' in col.lower()]

    # if not start_candidates or not end_candidates or 'sector' not in df_sample.columns:
    #     st.error("❌ Required columns not found. Make sure your table contains 'sector', a start price column (like 'start_price' or 'open_price'), and an end price column (like 'end_price' or 'close_price').")
    #     st.stop()

    # start_col = start_candidates[0]
    # end_col = end_candidates[0]

    # # Now fetch the full data with identified columns only
    # query = f"SELECT Sector, {start_col}, {end_col} FROM sectorwise_performance"
    # df = pd.read_sql(query, engine)

    # # Rename for convenience
    # df = df.rename(columns={start_col: 'start_price', end_col: 'end_price'})

    # # Calculate yearly return
    # df['Average_Yearly_Return'] = (df['end_price'] - df['start_price']) / df['start_price']

    # grouped_df = df.groupby('Sector')['Average_Yearly_Return'].mean().reset_index()
    # #grouped_df.rename(columns={'Average_Yearly_Return': 'avg_return'}, inplace=True)

    # st.subheader("📊 Sector-wise Performance")
    # col1, col2 = st.columns([1, 2])
    # with col1:
    #     st.dataframe(grouped_df)
    # with col2:
    #     fig = px.bar(
    #         grouped_df,
    #         x='Sector',
    #         y='Average_Yearly_Return',
    #         color='Average_Yearly_Return',
    #         text='Average_Yearly_Return',
    #         title="Sector-wise Avg Return",
    #         template='ggplot2',
    #         color_continuous_scale='Purples'
    #     )
    #     st.plotly_chart(fig, use_container_width=True)


def correlation_matrix():
    st.header("📊 Stock Price Correlation Heatmap")
    query = "SELECT * FROM correlation_matrix"
    df = pd.read_sql(query, engine)

    fig, ax = plt.subplots(figsize=(25, 20))
    sns.heatmap(
        df.set_index("Ticker"),
        cmap="coolwarm",
        annot=True,
        fmt=".2f",
        linewidths=0.5,
        ax=ax
    )
    st.pyplot(fig)


def top_gainers_losers():
    st.header("📅 Monthly Gainers & Losers")

    months_query = "SELECT DISTINCT month FROM top_gainers_losers ORDER BY month DESC"
    months = pd.read_sql(months_query, engine)["month"].tolist()
    selected_month = st.selectbox("Select a Month", months)

    df = pd.read_sql(
        f"SELECT * FROM top_gainers_losers WHERE month = '{selected_month}'",
        engine
    )

    top5 = {
        "Gainers": df.sort_values(by="monthly_return", ascending=False).head(5),
        "Losers": df.sort_values(by="monthly_return", ascending=True).head(5)
    }

    col1, col2 = st.columns(2)
    for col, label, color_scale in zip(
        [col1, col2],
        ["Gainers", "Losers"],
        ["Greens", "Reds"]
    ):
        with col:
            st.subheader(f"{'📈' if label == 'Gainers' else '📉'} Top 5 {label}")
            st.dataframe(top5[label])
            fig = px.bar(
                top5[label],
                x='Ticker',
                y='monthly_return',
                color='monthly_return',
                text='monthly_return',
                title=f"Top 5 {label}",
                template='plotly_white',
                color_continuous_scale=color_scale
            )
            st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Page Routing
# -------------------------------
pages = {
    "Home": home,
    "Volatility Analysis": volatility_analysis,
    "Cumulative Returns": top_5_cumulative_return,
    "Sector Performance": sectorwise_performance,
    "Stock Correlation": correlation_matrix,
    "Gainers & Losers": top_gainers_losers
}

# Execute selected page function
pages[selection]()
