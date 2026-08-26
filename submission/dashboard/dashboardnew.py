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


# ==================================================
# CONSTANTS
# ==================================================

DEMAND_COLORS = {
    "Low Demand": "#E74C3C",
    "Medium Demand": "#F1C40F",
    "High Demand": "#2ECC71",
}

USER_COLORS = {"Registered": "#72BCD4", "Casual": "#FFB703"}

CHART_LAYOUT = {"height": 400, "margin": dict(l=10, r=10, t=60, b=10)}


# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data
def load_data():
    daily_df = pd.read_csv("daily_df.csv")
    hourly_df = pd.read_csv("hourly_df.csv")
    daily_demand_df = pd.read_csv("daily_demand_group_df.csv")
    hourly_demand_df = pd.read_csv("hourly_demand_group_df.csv")

    daily_df["date"] = pd.to_datetime(daily_df["date"])
    hourly_df["date"] = pd.to_datetime(hourly_df["date"])

    return (daily_df, hourly_df, daily_demand_df, hourly_demand_df)


(daily_df, hourly_df, daily_demand_df, hourly_demand_df) = load_data()


# ==================================================
# KPI
# ==================================================
def calculate_kpis(df):
    return {
        "total": df["count"].sum(),
        "registered": df["registered"].sum(),
        "casual": df["casual"].sum(),
    }


def render_kpis(df):
    kpis = calculate_kpis(df)

    col1, col2, col3 = st.columns(3)

    col1.metric(label="Total Rentals", value=f"{kpis['total']:,.0f}")

    col2.metric(label="Registered", value=f"{kpis['registered']:,.0f}")

    col3.metric(label="Casual", value=f"{kpis['casual']:,.0f}")


# ==================================================
# CHART FIRST ROWS
# ==================================================
def format_chart(fig, show_legend=False):
    fig.update_layout(
        height=CHART_LAYOUT["height"],
        margin=CHART_LAYOUT["margin"],
        showlegend=show_legend,
    )

    return fig


def create_date_chart(df):
    chart_df = df.sort_values("date")

    fig = px.line(
        chart_df,
        x="date",
        y="count",
        title="Total Rentals by Date",
        labels={"date": "Date", "count": "Total Rentals"},
    )

    fig.update_traces(
        line_color="#72BCD4",
        line_width=2,
        hovertemplate=(
            "<b>Date: %{x|%d %B %Y}</b><br>Total Rentals: %{y:,.0f}<extra></extra>"
        ),
    )

    return format_chart(fig)


def create_weather_chart(df, analysis_type):
    weather_df = (
        df.groupby("weathersit", as_index=False, observed=False)
        .agg(average_rentals=("count", "mean"))
        .round({"average_rentals": 2})
        .sort_values("average_rentals", ascending=False)
    )

    fig = px.bar(
        weather_df,
        x="weathersit",
        y="average_rentals",
        color="average_rentals",
        color_continuous_scale="Blues",
        text_auto=".0f",
        title=f"Average {analysis_type} Rentals by Weather",
        labels={"weathersit": "Weather", "average_rentals": "Average Rentals"},
    )

    fig.update_traces(
        textposition="outside",
        hovertemplate=(
            "<b>Weather: %{x}</b><br>Average Rentals: %{y:,.2f}<extra></extra>"
        ),
    )

    fig.update_layout(coloraxis_showscale=False)

    return format_chart(fig)


daily_weather_fig = create_weather_chart(daily_df, "Daily")

hourly_weather_fig = create_weather_chart(hourly_df, "Hourly")


def create_user_type_chart(df, analysis_type):
    user_type_df = pd.DataFrame(
        {
            "user_type": ["Registered", "Casual"],
            "total_rentals": [df["registered"].sum(), df["casual"].sum()],
        }
    )

    fig = px.pie(
        user_type_df,
        names="user_type",
        values="total_rentals",
        color="user_type",
        color_discrete_map=USER_COLORS,
        hole=0.45,
        title=f"{analysis_type} Rentals by User Type",
    )

    fig.update_traces(
        textposition="inside",
        textinfo="label+percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Total: %{value:,.0f}<br>"
            "Percentage: %{percent}"
            "<extra></extra>"
        ),
    )

    return format_chart(fig)


def create_hourly_demand_chart(df):
    chart_df = df.sort_values("hour").copy()
    hour_order = chart_df["hour"].tolist()

    fig = px.bar(
        chart_df,
        x="hour",
        y="average",
        color="demand_group",
        color_discrete_map=DEMAND_COLORS,
        category_orders={"hour": hour_order},
        title="Average Rentals by Hour",
        labels={
            "hour": "Hour",
            "average": "Average Rentals",
            "demand_group": "Demand Group",
        },
    )

    fig.update_traces(
        hovertemplate=("<b>Hour: %{x}</b><br>Average Rentals: %{y:,.2f}<extra></extra>")
    )

    return format_chart(fig, show_legend=False)


def render_chart_row(figures):
    columns = st.columns(len(figures))

    for column, figure in zip(columns, figures):
        with column:
            st.plotly_chart(figure, width="stretch")


def render_daily_dashboard(daily_df):
    st.subheader("Daily Demand Analysis")

    render_kpis(daily_df)

    date_fig = create_date_chart(daily_df)

    weather_fig = create_weather_chart(daily_df, "Daily")

    user_fig = create_user_type_chart(daily_df, "Daily")

    render_chart_row([date_fig, weather_fig, user_fig])


def render_hourly_dashboard(hourly_df, hourly_demand_df):
    st.subheader("Hourly Demand Analysis")

    render_kpis(hourly_df)

    demand_fig = create_hourly_demand_chart(hourly_demand_df)

    weather_fig = create_weather_chart(hourly_df, "Hourly")

    user_fig = create_user_type_chart(hourly_df, "Hourly")

    render_chart_row([demand_fig, weather_fig, user_fig])


def main():
    st.title("Bike Sharing Demand Analytics")

    st.caption("Understanding Rental Patterns to Improve Operational Efficiency")

    st.sidebar.title("Navigation")

    analysis_type = st.sidebar.radio(
        "Analysis Type", options=["Daily", "Hourly"], horizontal=True
    )

    if analysis_type == "Daily":
        render_daily_dashboard(daily_df)

    else:
        render_hourly_dashboard(hourly_df, hourly_demand_df)


if __name__ == "__main__":
    main()
# # HELPER FUNCTIONS
# def total_rentals(df, column):
#     total = df[column].sum()
#     return total


# # Average daily rentals by weather
# weather_average_df = (
#     daily_df.groupby("weathersit", as_index=False, observed=False)
#     .agg(average_rentals=("count", "mean"))
#     .round({"average_rentals": 2})
#     .sort_values("average_rentals", ascending=False)
# )

# # Menyiapkan data komposisi pengguna
# daily_user_type_df = pd.DataFrame(
#     {
#         "user_type": ["Registered", "Casual"],
#         "total_rentals": [daily_df["registered"].sum(), daily_df["casual"].sum()],
#     }
# )


# # DASHBOARD

# # Title
# st.title("Bike Sharing Demand Analytics")
# st.subheader("Understanding Rental Patterns to Improve Operational Efficiency")

# # SIDEBAR
# st.sidebar.title("Navigation")

# # Filter
# analysis_type = st.sidebar.radio(
#     "Analysis Type", options=["Hourly", "Daily"], horizontal=True
# )


# # First Rows

# # KPI
# count = total_rentals(daily_df, "count")
# registered = total_rentals(daily_df, "count")
# casual = total_rentals(daily_df, "casual")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.metric(label="Total Rentals", value=f"{count:,.0f}")

# with col2:
#     st.metric(label="Registered", value=f"{registered:,.0f}")

# with col3:
#     st.metric(label="Casual", value=f"{casual:,.0f}")


# # Second Rows
# # Chart First Row
# chart_col1, chart_col2, chart_col3 = st.columns(3)

# demand_colors = {
#     "Low Demand": "#E74C3C",
#     "Medium Demand": "#F1C40F",
#     "High Demand": "#2ECC71",
# }

# hourly_demand_group_df = hourly_demand_group_df.sort_values("hour")

# hour_order = hourly_demand_group_df["hour"].tolist()

# chart_col1, chart_col2, chart_col3 = st.columns(3)


# with chart_col1:
#     fig_date = px.line(
#         daily_df,
#         x="date",
#         y="count",
#         title="Total Rentals by Date",
#         labels={"date": "Date", "count": "Total Rentals"},
#     )
#     fig_date.update_traces(
#         line_color="#72BCD4",
#         line_width=2,
#         hovertemplate=(
#             "<b>Date: %{x|%d %B %Y}</b><br>Total Rentals: %{y:,.0f}<extra></extra>"
#         ),
#     )
#     fig_date.update_layout(
#         height=400, margin=dict(l=10, r=10, t=60, b=10), showlegend=False
#     )
#     st.plotly_chart(fig_date, width="stretch")

# with chart_col2:
#     fig_weather = px.bar(
#         weather_average_df,
#         x="weathersit",
#         y="average_rentals",
#         title="Average Daily Rentals by Weather",
#         labels={
#             "weathersit": "Weather Condition",
#             "average_rentals": "Average Daily Rentals",
#         },
#         color="average_rentals",
#         color_continuous_scale="Blues",
#         text_auto=".0f",
#     )
#     fig_weather.update_traces(
#         textposition="outside",
#         hovertemplate=(
#             "<b>Weather: %{x}</b><br>Average Rentals: %{y:,.2f}<extra></extra>"
#         ),
#     )
#     fig_weather.update_layout(
#         height=400,
#         margin=dict(l=10, r=10, t=60, b=10),
#         coloraxis_showscale=False,
#         showlegend=False,
#         xaxis_title="Weather Condition",
#         yaxis_title="Average Daily Rentals",
#     )
#     st.plotly_chart(fig_weather, width="stretch")

# with chart_col3:
#     fig_weather = px.bar(
#         weather_average_df,
#         x="weathersit",
#         y="average_rentals",
#         title="Average Daily Rentals by Weather",
#         labels={
#             "weathersit": "Weather Condition",
#             "average_rentals": "Average Daily Rentals",
#         },
#         color="average_rentals",
#         color_continuous_scale="Blues",
#         text_auto=".0f",
#     )
#     fig_weather.update_traces(
#         textposition="outside",
#         hovertemplate=(
#             "<b>Weather: %{x}</b><br>Average Rentals: %{y:,.2f}<extra></extra>"
#         ),
#     )
#     fig_weather.update_layout(
#         height=400,
#         margin=dict(l=10, r=10, t=60, b=10),
#         coloraxis_showscale=False,
#         showlegend=False,
#         xaxis_title="Weather Condition",
#         yaxis_title="Average Daily Rentals",
#     )
#     st.plotly_chart(fig_weather, width="stretch")

# chart_col1, chart_col2, chart_col3 = st.columns(3)
# with chart_col1:
#     fig_pie = px.pie(
#         daily_user_type_df,
#         names="user_type",
#         values="total_rentals",
#         title="Daily Rentals by User Type",
#         color="user_type",
#         color_discrete_map={"Registered": "#72BCD4", "Casual": "#FFB703"},
#         hole=0.45,
#     )

#     fig_pie.update_traces(
#         textposition="inside",
#         textinfo="label+percent",
#         hovertemplate=(
#             "<b>%{label}</b><br>"
#             "Total Rentals: %{value:,.0f}<br>"
#             "Percentage: %{percent}"
#             "<extra></extra>"
#         ),
#     )

#     fig_pie.update_layout(
#         height=400, margin=dict(l=10, r=10, t=60, b=10), legend_title="User Type"
#     )

#     st.plotly_chart(fig_pie, width="stretch")

# with chart_col2:
#     fig_demand = px.bar(
#         hourly_demand_group_df,
#         x="hour",
#         y="average",
#         color="demand_group",
#         color_discrete_map=demand_colors,
#         category_orders={"hour": hour_order},
#         title="Average Rentals by Hour",
#         labels={
#             "hour": "Hour",
#             "average": "Average Rentals",
#             "demand_group": "Demand Group",
#         },
#     )
#     fig_demand.update_layout(
#         height=400, margin=dict(l=10, r=10, t=60, b=10), showlegend=False
#     )
#     st.plotly_chart(fig_demand, width="stretch")
