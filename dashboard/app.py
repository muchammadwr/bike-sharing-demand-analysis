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
    st.image("logo.png", width=200, output_format="PNG")

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

# Daily Tab
with daily_tab:
    daily_chart_line = px.line(
        filtered_daily_df,
        x="date",
        y="count",
        title="Daily Rental Trend",
        markers=True,
        labels={"date": "Date", "count": "Total Rentals"},
    )

    st.plotly_chart(daily_chart_line, use_container_width=True)

    # Chart firs row
    chart1, chart2 = st.columns(2)

    # Monthly Chart
    with chart1:
        month_order = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        avg_monthly = (
            filtered_daily_df.groupby("month")["count"].agg(["mean"]).reset_index()
        )

        avg_monthly["month"] = pd.Categorical(
            avg_monthly["month"], categories=month_order, ordered=True
        )

        avg_monthly = avg_monthly.sort_values("month")

        monthly_chart = px.bar(
            avg_monthly,
            x="month",
            y="mean",
            title="Average Rental Demand by Month",
            labels={"month": "Month", "average_rentals": "Average Rentals"},
        )

        st.plotly_chart(monthly_chart, use_container_width=True)

    with chart2:
        # Avg. Temperature
        temperature_chart = px.scatter(
            filtered_daily_df,
            x="temperature",
            y="count",
            title="Rental Demand by Temperature",
            labels={"temperature": "Temperature (°C)", "count": "Total Rentals"},
            opacity=0.7,
            trendline="ols",
        )

        st.plotly_chart(temperature_chart, use_container_width=True)

    # Chart second Row
    chart3, chart4 = st.columns(2)

    with chart3:
        # Avg Daily by Weather
        avg_daily_rentals_by_weathersit = (
            filtered_daily_df.groupby("weathersit")["count"].agg(["mean"]).reset_index()
        )
        avg_daily_rentals_by_weathersit_chart = px.bar(
            avg_daily_rentals_by_weathersit,
            x="weathersit",
            y="mean",
            title="Average Rental by Weathersit",
            labels={"weathersit": "Weather", "mean": "Average"},
        )
        st.plotly_chart(avg_daily_rentals_by_weathersit_chart, use_container_width=True)

    with chart4:
        # Avg Daily by Weather
        avg_daily_rentals_by_season = (
            filtered_daily_df.groupby("season")["count"].agg(["mean"]).reset_index()
        )
        avg_daily_rentals_by_season_chart = px.bar(
            avg_daily_rentals_by_season,
            x="season",
            y="mean",
            title="Average Rental by Season",
            labels={"season": "Season", "mean": "Average"},
        )
        st.plotly_chart(avg_daily_rentals_by_season_chart, use_container_width=True)

    # Chart Third Row
    chart5, chart6 = st.columns(2)

    # Casual vs Registered
    with chart5:
        user_type_df = pd.DataFrame(
            {
                "user_type": ["Registered", "Casual"],
                "total": [
                    filtered_daily_df["registered"].sum(),
                    filtered_daily_df["casual"].sum(),
                ],
            }
        )

        fig_usertype = px.pie(
            user_type_df,
            names="user_type",
            values="total",
            title="Bike Rentals by User Type",
        )

        st.plotly_chart(fig_usertype, use_container_width=True)

    # Grouping base on Low, Medium, and High demand
    with chart6:
        weekday_order = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        demand_labels = ["Low", "Medium", "High"]
        segment_colors = {
            "Low": "#EF553B",
            "Medium": "#FFA15A",
            "High": "#00CC96",
        }

        weekday_baseline = daily_df.groupby("weekday", as_index=False).agg(
            average=("count", "mean")
        )

        # Fixed thresholds based on full dataset
        low_threshold = weekday_baseline["average"].quantile(1 / 3)
        high_threshold = weekday_baseline["average"].quantile(2 / 3)

        # Calculate demand from filtered dataset
        weekday_demand = (
            filtered_daily_df.groupby("weekday", as_index=False)
            .agg(total=("count", "sum"), average=("count", "mean"))
            .round(2)
        )

        # Classify filtered demand using fixed thresholds
        weekday_demand["demand"] = pd.cut(
            weekday_demand["average"],
            bins=[-float("inf"), low_threshold, high_threshold, float("inf")],
            labels=demand_labels,
            include_lowest=True,
        )

        fig_seg = px.bar(
            weekday_demand,
            x="weekday",
            y="average",
            color="demand",
            color_discrete_map=segment_colors,
            category_orders={"weekday": weekday_order, "demand": demand_labels},
            title="Average Bike Rental Demand by Weekday",
            labels={
                "weekday": "Weekday",
                "average": "Average Rentals",
                "demand": "Demand Group",
            },
        )

        fig_seg.update_traces(texttemplate="%{y:.0f}", textposition="outside")

        st.plotly_chart(fig_seg, use_container_width=True)


# Hourly Tab
with hourly_tab:
    # Demand by hourly
    hourly_demand = filtered_hourly_df.groupby("hour")["count"].sum().reset_index()
    hourly_chart_line = px.line(
        hourly_demand,
        x="hour",
        y="count",
        title="Daily Rental Trend",
        markers=True,
        labels={"date": "Hour", "count": "Total Rentals"},
    )
    st.plotly_chart(hourly_chart_line, use_container_width=True)

    chart1, chart2 = st.columns(2)

    # Temperature hourly
    with chart1:
        avg_temperature_hourly = filtered_hourly_df.groupby("hour", as_index=False)[
            "temperature"
        ].agg(["mean"])
        temperature_chart = px.scatter(
            avg_temperature_hourly,
            x="hour",
            y="mean",
            title="Temperature",
            labels={"temperature": "Temperature (°C)", "avg": "Total Rentals"},
        )

        st.plotly_chart(temperature_chart, use_container_width=True)

    # Humidity hourly
    with chart2:
        avg_humidity = filtered_hourly_df.groupby("hour", as_index=False)[
            "humidity"
        ].agg(["mean"])
        temperature_chart = px.scatter(
            avg_temperature_hourly,
            x="hour",
            y="mean",
            title="Humidity",
            labels={"temperature": "Temperature (°C)", "avg": "Total Rentals"},
        )

        st.plotly_chart(temperature_chart, use_container_width=True)

    chart3, chart4 = st.columns(2)
    with chart3:
        avg_windspeed = filtered_hourly_df.groupby("hour", as_index=False)[
            "windspeed"
        ].agg(["mean"])
        temperature_chart = px.scatter(
            avg_windspeed,
            x="hour",
            y="mean",
            title="Windspeed",
            labels={"temperature": "Temperature (°C)", "avg": "Total Rentals"},
        )

        st.plotly_chart(temperature_chart, use_container_width=True)

    with chart4:
        demand_labels = ["Low", "Medium", "High"]

        segment_colors = {
            "Low": "#EF553B",
            "Medium": "#FFA15A",
            "High": "#00CC96",
        }

        hour_order = [f"{hour:02d}:00" for hour in range(24)]

        # Calculate baseline average demand
        hourly_baseline = hourly_df.groupby("hour", as_index=False).agg(
            average=("count", "mean")
        )

        # Fixed thresholds
        low_threshold = hourly_baseline["average"].quantile(1 / 3)
        high_threshold = hourly_baseline["average"].quantile(2 / 3)

        # Calculate filtered hourly demand
        hourly_demand = (
            filtered_hourly_df.groupby("hour", as_index=False)
            .agg(total=("count", "sum"), average=("count", "mean"))
            .round(2)
        )

        # Create readable hour labels
        hourly_demand["hour_label"] = hourly_demand["hour"].astype(str).str.slice(0, 5)

        # Classify demand
        hourly_demand["demand"] = pd.cut(
            hourly_demand["average"],
            bins=[-float("inf"), low_threshold, high_threshold, float("inf")],
            labels=demand_labels,
            include_lowest=True,
        )

        # Create chart
        fig_seg = px.bar(
            hourly_demand,
            x="hour_label",
            y="average",
            color="demand",
            color_discrete_map=segment_colors,
            category_orders={
                "hour_label": hour_order,
                "demand": demand_labels,
            },
            title="Average Bike Rental Demand by Hour",
            labels={
                "hour_label": "Hour",
                "average": "Average Rentals",
                "demand": "Demand Group",
            },
        )

        fig_seg.update_traces(texttemplate="%{y:.0f}", textposition="outside")

        st.plotly_chart(fig_seg, use_container_width=True)
