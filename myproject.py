import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

st.set_page_config(layout="wide", page_title="Agri-Commodity Market Dashboard")

st.title(" Agri-Commodity Market Analytics Dashboard")

# === Load Data ===
@st.cache_data
def load_data():
    df = pd.read_csv("dataset.csv")
    df['Arrival_Date'] = pd.to_datetime(df['Arrival_Date'], dayfirst=True)
    return df

df = load_data()

# === SIDEBAR FILTERS ===
with st.sidebar:
    st.header(" Filters")
    states = st.multiselect("Select State(s)", df["State"].unique(), default=df["State"].unique())
    commodities = st.multiselect("Select Commodity", df["Commodity"].unique(), default=df["Commodity"].unique())
    date_range = st.date_input("Select Date Range", [df["Arrival_Date"].min(), df["Arrival_Date"].max()])

# Apply filters
mask = (
    df["State"].isin(states) &
    df["Commodity"].isin(commodities) &
    (df["Arrival_Date"] >= pd.to_datetime(date_range[0])) &
    (df["Arrival_Date"] <= pd.to_datetime(date_range[1]))
)
filtered_df = df[mask]

# === Analysis Type Selector ===
analysis_type = st.radio(" Select Analysis Type", [
    "Overview",
    "Commodity-wise Analysis",
    "State-wise Analysis",
    "Time Series Trend",
    "Distribution Plots"
])

# === OVERVIEW ===
if analysis_type == "Overview":
    st.header(" Dataset Overview")
    
    if filtered_df.empty:
        st.warning("No data found for the selected filters.")
    else:
        st.subheader(" Filtered Data (Top 100 Rows)")
        st.dataframe(filtered_df.head(100))

        st.subheader(" Price Summary Statistics")
        st.dataframe(filtered_df[["Min Price", "Max Price", "Modal Price"]].describe())

        if st.button(" Show Price Correlation Heatmap"):
            fig, ax = plt.subplots()
            sns.heatmap(filtered_df[["Min Price", "Max Price", "Modal Price"]].corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)

# === COMMODITY-WISE ANALYSIS ===
elif analysis_type == "Commodity-wise Analysis":
    st.header(" Commodity Insights")
    if filtered_df.empty:
        st.warning("No data available for analysis.")
    else:
        commodity = st.selectbox("Select a Commodity", sorted(filtered_df["Commodity"].unique()))
        subset = filtered_df[filtered_df["Commodity"] == commodity]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(" Average Prices")
            avg_prices = subset[["Min Price", "Max Price", "Modal Price"]].mean()
            st.bar_chart(avg_prices)

        with col2:
            st.subheader(" Price Trend Over Time")
            time_series = subset.groupby("Arrival_Date")["Modal Price"].mean().reset_index()
            fig, ax = plt.subplots()
            sns.lineplot(data=time_series, x="Arrival_Date", y="Modal Price", ax=ax)
            ax.set_ylabel("Avg Modal Price")
            plt.xticks(rotation=45)
            st.pyplot(fig)

# === STATE-WISE ANALYSIS ===
elif analysis_type == "State-wise Analysis":
    st.header(" State-wise Market Analysis")
    if filtered_df.empty:
        st.warning("No data available for selected filters.")
    else:
        state = st.selectbox("Select a State", sorted(filtered_df["State"].unique()))
        state_df = filtered_df[filtered_df["State"] == state]

        st.subheader(" Top 10 Commodities by Modal Price")
        top10 = state_df.groupby("Commodity")["Modal Price"].mean().sort_values(ascending=False).head(10)
        st.bar_chart(top10)

        if st.button(" Show State vs Commodity Heatmap"):
            pivot = state_df.pivot_table(index="District", columns="Commodity", values="Modal Price", aggfunc="mean", fill_value=0)
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.heatmap(pivot, cmap="YlOrBr", ax=ax)
            st.pyplot(fig)

# === TIME SERIES ANALYSIS ===
elif analysis_type == "Time Series Trend":
    st.header(" Time Series Price Trends")
    if filtered_df.empty:
        st.warning("No data available.")
    else:
        selected = st.selectbox("Select Commodity for Trend", sorted(filtered_df["Commodity"].unique()))
        temp = filtered_df[filtered_df["Commodity"] == selected].groupby("Arrival_Date")["Modal Price"].mean().reset_index()

        fig, ax = plt.subplots()
        sns.lineplot(data=temp, x="Arrival_Date", y="Modal Price", ax=ax)
        ax.set_ylabel("Avg Modal Price")
        plt.xticks(rotation=45)
        st.pyplot(fig)

# === DISTRIBUTION PLOTS ===
elif analysis_type == "Distribution Plots":
    st.header(" Price Distribution")
    if filtered_df.empty:
        st.warning("No data found.")
    else:
        feature = st.radio("Choose a Price Type", ["Min Price", "Max Price", "Modal Price"])
        fig, ax = plt.subplots()
        sns.histplot(filtered_df[feature], kde=True, color="skyblue", ax=ax)
        ax.set_title(f"{feature} Distribution")
        st.pyplot(fig)
