import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px


# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
st.title("🚲 Bike Sharing Demand Analytics")
st.subheader("Understanding Rental Patterns to Improve Operational Efficiency")

# ==================================================
# LOAD DATA
# ==================================================


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df


daily_df = load_data("daily_df.csv")
hourly_df = load_data("hourly_df.csv")

# Convert date columns
daily_df["date"] = pd.to_datetime(daily_df["date"])
hourly_df["date"] = pd.to_datetime(hourly_df["date"])

# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.title("Navigation")

    min_date = daily_df["date"].min().date()
    max_date = daily_df["date"].max().date()

    selected_dates = st.date_input(
        label="Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )


# ==================================================
# VALIDATE DATE RANGE
# ==================================================

if len(selected_dates) != 2:
    st.warning("Please select both start and end dates.")
    st.stop()

start_date, end_date = selected_dates

if start_date > end_date:
    st.error("Start date cannot be later than end date.")
    st.stop()


# ==================================================
# FILTER DATA
# ==================================================

filtered_daily_df = daily_df[
    daily_df["date"].dt.date.between(start_date, end_date, inclusive="both")
].copy()

filtered_hourly_df = hourly_df[
    hourly_df["date"].dt.date.between(start_date, end_date, inclusive="both")
].copy()

st.caption(
    f"Period: {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}"
)

# ==================================================
# KPI
# ==================================================

total_rentals = filtered_daily_df["count"].sum()
casual_rentals = filtered_daily_df["casual"].sum()
registered_rentals = filtered_daily_df["registered"].sum()

if total_rentals > 0:
    registered_share = registered_rentals / total_rentals * 100
    casual_share = casual_rentals / total_rentals * 100
else:
    registered_share = 0
    casual_share = 0


kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric(
        label="🚲 Total Rentals",
        value=f"{total_rentals:,.0f}",
        help="Total bike rentals during the selected period.",
    )

with kpi2:
    st.metric(
        label="👤 Registered Rentals",
        value=f"{registered_rentals:,.0f}",
        delta=f"{registered_share:.1f}% of total",
        help="Rentals made by registered users.",
    )

with kpi3:
    st.metric(
        label="🌍 Casual Rentals",
        value=f"{casual_rentals:,.0f}",
        delta=f"{casual_share:.1f}% of total",
        help="Rentals made by casual users.",
    )


# ==================================================
# CHART FIRST ROW
# ==================================================

hourly_summary = filtered_hourly_df.groupby("hour", as_index=False).agg(
    average_rentals=("count", "mean")
)

user_summary = pd.DataFrame(
    {
        "user_type": ["Registered", "Casual"],
        "total_rentals": [registered_rentals, casual_rentals],
    }
)


chart1, chart2, chart3 = st.columns(3)

with chart1:
    daily_chart = px.line(
        filtered_daily_df,
        x="date",
        y="count",
        title="Daily Rental Trend",
        labels={"date": "Date", "count": "Total Rentals"},
    )

    st.plotly_chart(daily_chart, use_container_width=True)

with chart2:
    hourly_chart = px.bar(
        hourly_summary,
        x="hour",
        y="average_rentals",
        title="Average Rentals by Hour",
        labels={"hour": "Hour", "average_rentals": "Average Rentals"},
    )

    hourly_chart.update_xaxes(dtick=1)

    st.plotly_chart(hourly_chart, use_container_width=True)

with chart3:
    user_chart = px.pie(
        user_summary,
        names="user_type",
        values="total_rentals",
        title="Rentals by User Type",
        hole=0.4,
    )

    st.plotly_chart(user_chart, use_container_width=True)
