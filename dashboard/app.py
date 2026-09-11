import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px


# PAGE CONFIGURATION

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

st.title("🚲 Bike Sharing Demand Analytics")
st.subheader("Understanding Rental Patterns to Improve Operational Efficiency")


# LOAD DATA
@st.cache_data
def load_data(path):
    return pd.read_csv(path)


daily_df = load_data("daily_df.csv")
hourly_df = load_data("hourly_df.csv")

# DATA PREPARATION

# Convert date columns
daily_df["date"] = pd.to_datetime(daily_df["date"])
hourly_df["date"] = pd.to_datetime(hourly_df["date"])


# FILTER RANGE SETUP
min_date = daily_df["date"].min().date()
max_date = daily_df["date"].max().date()

# SIDEBAR FILTERS
with st.sidebar:
    st.image("logo.png", width="content", output_format="PNG")

    st.title("Navigation")

    # Date filter
    selected_dates = st.date_input(
        label="Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Validate date range
    if len(selected_dates) != 2:
        st.warning("Please select both start and end dates.")
        st.stop()

    start_date, end_date = selected_dates

    if start_date > end_date:
        st.error("Start date cannot be later than end date.")
        st.stop()

    # Year filter
    selected_year = st.multiselect(
        "Year",
        options=sorted(daily_df["year"].dropna().unique()),
        default=sorted(daily_df["year"].dropna().unique()),
    )

    # Season filter
    selected_season = st.multiselect(
        "Season",
        options=daily_df["season"].dropna().unique(),
        default=daily_df["season"].dropna().unique(),
    )

    # Weather filter
    selected_weather = st.multiselect(
        "Weather",
        options=daily_df["weathersit"].dropna().unique(),
        default=daily_df["weathersit"].dropna().unique(),
    )

    # Weekday filter
    selected_weekday = st.multiselect(
        "Weekday",
        options=daily_df["weekday"].dropna().unique(),
        default=daily_df["weekday"].dropna().unique(),
    )


# APPLY FILTERS
filtered_daily_df = daily_df[
    daily_df["date"].dt.date.between(start_date, end_date, inclusive="both")
    & daily_df["year"].isin(selected_year)
    & daily_df["season"].isin(selected_season)
    & daily_df["weathersit"].isin(selected_weather)
    & daily_df["weekday"].isin(selected_weekday)
].copy()


filtered_hourly_df = hourly_df[
    hourly_df["date"].dt.date.between(start_date, end_date, inclusive="both")
    & hourly_df["year"].isin(selected_year)
    & hourly_df["season"].isin(selected_season)
    & hourly_df["weathersit"].isin(selected_weather)
    & hourly_df["weekday"].isin(selected_weekday)
].copy()


# VALIDATE FILTERED DATA

if filtered_daily_df.empty:
    st.warning("No daily data is available for the selected filters.")
    st.stop()

if filtered_hourly_df.empty:
    st.warning("No hourly data is available for the selected filters.")
    st.stop()

# KPI CALCULATION
total_rentals = filtered_daily_df["count"].sum()
registered_rentals = filtered_daily_df["registered"].sum()
casual_rentals = filtered_daily_df["casual"].sum()

# Calculate rental shares
if total_rentals > 0:
    registered_share = registered_rentals / total_rentals * 100

    casual_share = casual_rentals / total_rentals * 100
else:
    registered_share = 0
    casual_share = 0

# KPI DISPLAY
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


daily_tab, hourly_tab = st.tabs(["📅 Daily Analysis", "⏰ Hourly Analysis"])

daily_chart = px.line(
    filtered_daily_df,
    x="date",
    y="count",
    title="Daily Rental Trend",
    markers=True,
    labels={"date": "Date", "count": "Total Rentals"},
)

st.plotly_chart(daily_chart, use_container_width=True)
