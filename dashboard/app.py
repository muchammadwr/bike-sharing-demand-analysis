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


daily_df["date"] = pd.to_datetime(daily_df["date"])
hourly_df["date"] = pd.to_datetime(hourly_df["date"])

# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.image("logo.png", width="content", output_format="PNG")
    st.title("Navigation")

    # ----------------------------------------------
    # Date filter
    # ----------------------------------------------

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

    selected_year = st.multiselect(
        "Year",
        options=daily_df["year"].unique(),
        default=daily_df["year"].unique(),
    )

    selected_season = st.sidebar.multiselect(
        "Season",
        options=daily_df["season"].unique(),
        default=daily_df["season"].unique(),
    )

    selected_weather = st.sidebar.multiselect(
        "Weather",
        options=daily_df["weathersit"].unique(),
        default=daily_df["weathersit"].unique(),
    )

    selected_weekday = st.sidebar.multiselect(
        "Weekday",
        options=daily_df["weekday"].unique(),
        default=daily_df["weekday"].unique(),
    )
    # =========================
    # APPLY FILTERS
    # =========================

# ==================================================
# KPI
# ==================================================
total_rentals = filtered_daily_df["count"].sum()
casual_rentals = filtered_daily_df["casual"].sum()
registered_rentals = filtered_daily_df["registered"].sum()

if filtered_daily_df.empty:
    st.warning("No data is available for the selected filters.")
    st.stop()

daily_df["season"] = daily_df["season"].replace({"Springer": "Spring"})

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
