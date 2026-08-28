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


# ==================================================
# TABS
# ==================================================

daily_tab, hourly_tab = st.tabs(["📅 Daily Analysis", "⏰ Hourly Analysis"])


# ==================================================
# DAILY TAB
# ==================================================

with daily_tab:
    st.subheader("Daily Rental Analysis")

    # ------------------------------------------------
    # TOP CHART: DAILY RENTAL TREND
    # ------------------------------------------------

    daily_chart = px.line(
        filtered_daily_df,
        x="date",
        y="count",
        title="Daily Rental Trend",
        markers=True,
        labels={"date": "Date", "count": "Total Rentals"},
    )

    st.plotly_chart(daily_chart, use_container_width=True)

    # ==================================================
    # MIDDLE ROW DATA PREPARATION
    # ==================================================

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

    # Average rentals by month
    monthly_summary = filtered_daily_df.groupby("month", as_index=False).agg(
        average_rentals=("count", "mean")
    )

    monthly_summary["month"] = pd.Categorical(
        monthly_summary["month"], categories=month_order, ordered=True
    )

    monthly_summary = monthly_summary.sort_values("month")

    # Average rentals by weather condition
    weather_summary = (
        filtered_daily_df.groupby("weathersit", as_index=False)
        .agg(average_rentals=("count", "mean"))
        .sort_values(by="average_rentals", ascending=False)
    )

    # ==================================================
    # MIDDLE ROW: THREE CHARTS
    # ==================================================

    middle_chart1, middle_chart2, middle_chart3 = st.columns(3)

    # ------------------------------------------------
    # CHART 1: RENTALS BY MONTH
    # ------------------------------------------------

    with middle_chart1:
        monthly_chart = px.bar(
            monthly_summary,
            x="month",
            y="average_rentals",
            title="Average Rental Demand by Month",
            labels={"month": "Month", "average_rentals": "Average Rentals"},
        )

        monthly_chart.update_layout(xaxis_tickangle=-45)

        st.plotly_chart(monthly_chart, use_container_width=True)

    # ------------------------------------------------
    # CHART 2: RENTALS BY WEATHER
    # ------------------------------------------------

    with middle_chart2:
        weather_chart = px.bar(
            weather_summary,
            x="weathersit",
            y="average_rentals",
            title="Average Rental Demand by Weather",
            labels={
                "weathersit": "Weather Condition",
                "average_rentals": "Average Rentals",
            },
        )

        weather_chart.update_layout(xaxis_tickangle=-25)

        st.plotly_chart(weather_chart, use_container_width=True)

    # ------------------------------------------------
    # CHART 3: RENTALS BY TEMPERATURE
    # ------------------------------------------------

    with middle_chart3:
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


# ==================================================
# BOTTOM ROW DATA PREPARATION
# ==================================================

# User type composition
user_summary = pd.DataFrame(
    {
        "user_type": ["Registered", "Casual"],
        "total_rentals": [registered_rentals, casual_rentals],
    }
)


# Weekday demand aggregation
weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

weekday_summary = filtered_daily_df.groupby("weekday", as_index=False).agg(
    average_rentals=("count", "mean")
)


# ==================================================
# QUANTILE SEGMENTATION
# ==================================================

weekday_q33 = weekday_summary["average_rentals"].quantile(0.33)
weekday_q67 = weekday_summary["average_rentals"].quantile(0.67)

weekday_summary["demand_segment"] = np.select(
    [
        weekday_summary["average_rentals"] <= weekday_q33,
        weekday_summary["average_rentals"] <= weekday_q67,
    ],
    ["Low Demand", "Medium Demand"],
    default="High Demand",
)


# Sort weekday chronologically
weekday_summary["weekday"] = pd.Categorical(
    weekday_summary["weekday"], categories=weekday_order, ordered=True
)

weekday_summary = weekday_summary.sort_values("weekday")


# Segment colors
segment_colors = {
    "Low Demand": "#EF553B",
    "Medium Demand": "#FFA15A",
    "High Demand": "#00CC96",
}

# ==================================================
# BOTTOM ROW: TWO CHARTS
# ==================================================

bottom_chart1, bottom_chart2 = st.columns(2)


# ------------------------------------------------
# USER TYPE PIE CHART
# ------------------------------------------------

with bottom_chart1:
    user_chart = px.pie(
        user_summary,
        names="user_type",
        values="total_rentals",
        title="Rental Composition by User Type",
        hole=0.4,
        color="user_type",
        color_discrete_map={"Registered": "#636EFA", "Casual": "#00CC96"},
    )

    user_chart.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Total Rentals: %{value:,.0f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
    )

    st.plotly_chart(user_chart, use_container_width=True)


# ------------------------------------------------
# WEEKDAY DEMAND SEGMENTATION
# ------------------------------------------------

with bottom_chart2:
    weekday_chart = px.bar(
        weekday_summary,
        x="weekday",
        y="average_rentals",
        color="demand_segment",
        title="Rental Demand Segmentation by Weekday",
        labels={
            "weekday": "Weekday",
            "average_rentals": "Average Rentals",
            "demand_segment": "Demand Segment",
        },
        color_discrete_map=segment_colors,
        category_orders={
            "weekday": weekday_order,
            "demand_segment": ["Low Demand", "Medium Demand", "High Demand"],
        },
        text_auto=".0f",
    )

    weekday_chart.update_traces(
        textposition="outside",
        hovertemplate=("<b>%{x}</b><br>Average Rentals: %{y:,.2f}<extra></extra>"),
    )

    weekday_chart.update_layout(yaxis_title="Average Rentals", xaxis_title="Weekday")

    st.plotly_chart(weekday_chart, use_container_width=True)

    st.caption(
        f"Low: ≤ {weekday_q33:,.0f} | "
        f"Medium: {weekday_q33:,.0f}–{weekday_q67:,.0f} | "
        f"High: > {weekday_q67:,.0f}"
    )

# ==================================================
# USER DEMAND SEGMENTATION
# ==================================================

segmented_daily_df = filtered_daily_df.copy()


def create_demand_segment(df, column):
    q33 = df[column].quantile(0.33)
    q67 = df[column].quantile(0.67)

    segment = pd.cut(
        df[column],
        bins=[float("-inf"), q33, q67, float("inf")],
        labels=["Low Demand", "Medium Demand", "High Demand"],
        include_lowest=True,
    )

    return segment, q33, q67


# Registered segmentation
(segmented_daily_df["registered_segment"], registered_q33, registered_q67) = (
    create_demand_segment(segmented_daily_df, "registered")
)


# Casual segmentation
(segmented_daily_df["casual_segment"], casual_q33, casual_q67) = create_demand_segment(
    segmented_daily_df, "casual"
)


# Consistent colors for both charts
segment_colors = {
    "Low Demand": "#EF553B",
    "Medium Demand": "#FFA15A",
    "High Demand": "#00CC96",
}

segment_order = ["Low Demand", "Medium Demand", "High Demand"]


# ==================================================
# HOURLY TAB
# ==================================================
