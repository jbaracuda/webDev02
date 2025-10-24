import streamlit as st
import pandas as pd
import numpy as np
import json # The 'json' module is needed to work with JSON files.
import os   # The 'os' module helps with file system operations.

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Visualizations",
    page_icon="📈",
)

# PAGE TITLE AND INFORMATION
st.title("Data Visualizations 📈")
st.write("This page displays graphs based on the collected data.")

st.divider()
st.header("Load Data")

csv_data = pd.DataFrame()
json_data = []

if os.path.exists("data.csv"):
    try:
        csv_data = pd.read_csv("data.csv")
        st.success("Loaded data.csv successfully")
    except Exception as e:
        st.error(f"Error loading data.csv: {e}")
else:
    st.warning("data.csv not found")

if os.path.exists("data.json"):
    try:
        with open("data.json", "r") as f:
            json_data = json.load(f)
        st.success("Loaded data.json successfully")
    except Exception as e:
        st.error(f"Error loading data.json: {e}")
else:
    st.warning("data.json not found")

st.divider()
st.header("Graphs")

# GRAPH 1: METRICS FOR RECOMMENDED, GOAL, AND DAILY INTAKE
st.subheader("Graph 1: Macronutrient Metrics")

def load_csv(file):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=["Metric", "Calories", "Protein", "Carbs", "Fat"])

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            try:
                return pd.DataFrame(json.load(f))
            except json.JSONDecodeError:
                return pd.DataFrame(columns=["Metric", "Calories", "Protein", "Carbs", "Fat"])
    return pd.DataFrame(columns=["Metric", "Calories", "Protein", "Carbs", "Fat"])

csv_df = load_csv("data.csv")
json_df = load_json("data.json")
df = pd.concat([csv_df, json_df]).drop_duplicates(subset=["Metric"], keep="last")
df_grouped = df.set_index("Metric")

metrics_to_display = ["Recommended", "Goal", "Intake"]
nutrients = ["Calories", "Protein", "Carbs", "Fat"]
available_metrics = [m for m in metrics_to_display if m in df_grouped.index]
display_df = df_grouped.loc[available_metrics, nutrients] if available_metrics else pd.DataFrame()

if not display_df.empty:
    for nutrient in nutrients:
        rec_value = display_df.loc["Recommended", nutrient] if "Recommended" in display_df.index else 0
        if "Goal" in display_df.index:
            goal_value = display_df.loc["Goal", nutrient]
            goal_diff = ((goal_value - rec_value) / rec_value * 100) if rec_value else 0
            st.metric(
                label=f"Goal {nutrient}",
                value=f"{goal_value:.1f}",
                delta=f"{goal_diff:+.1f}% vs Recommended"
            )
        if "Intake" in display_df.index:
            intake_value = display_df.loc["Intake", nutrient]
            intake_diff = ((intake_value - rec_value) / rec_value * 100) if rec_value else 0
            st.metric(
                label=f"Daily Intake {nutrient}",
                value=f"{intake_value:.1f}",
                delta=f"{intake_diff:+.1f}% vs Recommended"
            )
        if "Recommended" in display_df.index:
            st.metric(
                label=f"Recommended {nutrient}",
                value=f"{rec_value:.1f}"
            )
else:
    st.warning("No data available to display for Recommended, Goal, or Daily Intake metrics.")

# GRAPH 2: PROJECTED WEIGHT CHANGE OVER WEEKS
st.subheader("Graph 2: Projected Weight Change Over Time")

goal_row = csv_df[csv_df["Metric"] == "Goal"].iloc[0] if not csv_df[csv_df["Metric"] == "Goal"].empty else None
intake_row = csv_df[csv_df["Metric"] == "Intake"].iloc[0] if not csv_df[csv_df["Metric"] == "Intake"].empty else None
body_info = json_df[json_df["Metric"] == "Goal and Info"].iloc[0] if not json_df[json_df["Metric"] == "Goal and Info"].empty else None

if goal_row is not None and intake_row is not None and body_info is not None:
    weeks = st.slider("Select number of weeks to project", 1, 52, 12)
    weight = body_info["Weight"]
    daily_surplus_goal = 0
    daily_surplus_intake = intake_row["Calories"] - goal_row["Calories"]
    weekly_change_goal = daily_surplus_goal * 7 / 3500
    weekly_change_intake = daily_surplus_intake * 7 / 3500
    week_numbers = range(1, weeks + 1)
    projected_weight_goal = [round(weight - w * weekly_change_goal) for w in week_numbers]
    projected_weight_intake = [round(weight - w * weekly_change_intake) for w in week_numbers]
    df_proj = pd.DataFrame({
        "Week": week_numbers,
        "Goal Projection": projected_weight_goal,
        "Intake Projection": projected_weight_intake
    }).set_index("Week")
    st.line_chart(df_proj)
else:
    st.warning("Please submit your body info, goal, and daily intake to generate the weight projection.")


# GRAPH 3: DYNAMIC GRAPH USING JSON DATA
st.subheader("Graph 3: Macro and Calorie Comparison")

json_metrics = [m for m in json_df["Metric"].tolist()] if not json_df.empty else []
# Remove 'Goal and Info' from the selection
json_metrics = [m for m in json_metrics if m != "Goal and Info"]

json_nutrients = ["Calories", "Protein", "Carbs", "Fat"]

if "json_selected_metrics" not in st.session_state:
    st.session_state.json_selected_metrics = json_metrics
if "json_selected_nutrients" not in st.session_state:
    st.session_state.json_selected_nutrients = ["Calories", "Protein"]

st.session_state.json_selected_metrics = st.multiselect(
    "Select metrics from JSON",
    options=json_metrics,
    default=st.session_state.json_selected_metrics
)

st.session_state.json_selected_nutrients = st.multiselect(
    "Select nutrients from JSON",
    options=json_nutrients,
    default=st.session_state.json_selected_nutrients
)

json_display_df = json_df.set_index("Metric").loc[
    st.session_state.json_selected_metrics,
    st.session_state.json_selected_nutrients
] if not json_df.empty else pd.DataFrame()

if not json_display_df.empty:
    st.bar_chart(json_display_df)
    st.caption("Dynamic bar chart using JSON data.")
else:
    st.warning("No JSON data available for the selected options.")
