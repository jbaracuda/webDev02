import streamlit as st
import pandas as pd
import os
import json

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Survey",
    page_icon="📝",
)

# PAGE TITLE AND USER DIRECTIONS
st.title("🥗 Macronutrient Survey")
st.write("Please fill out the form below to add your data to the dataset.")

def save_to_files(new_entry):
    # Load existing data
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Remove old entries with the same Metric
    data = [entry for entry in data if entry.get("Metric") != new_entry["Metric"]]
    data.append(new_entry)

    # Save JSON
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

    # Save CSV
    csv_file = "data.csv"
    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        df = pd.read_csv(csv_file)
        df = df[df["Metric"] != new_entry["Metric"]]
    else:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(csv_file, index=False)

# DATA INPUT FORM
st.subheader("💪Body Composition Info and Goals")

with st.form("body_form"):
    height = st.number_input("What is your height in inches?")
    weight = st.number_input("What is your weight in pounds?")
    age = st.number_input("How old are you?")
    goal = st.radio(
        "Are you bulking, cutting, or maintaining?",
        ["Bulking", "Cutting", "Maintain"]
    )

    submitted_body_info = st.form_submit_button("Submit Body Info and Goals")

if submitted_body_info:
    # Calculate recommended calories and macros
    if goal == "Bulking":
        rCal = (((6.23 * weight) + (12.7 * height) - (6.8 * age + 66)) * 1.55) + weight * 3.2
        rProtein = weight * 1.2
        rCarb = weight * 1.4
        rFat = weight * 0.4
    elif goal == "Cutting":
        rCal = ((6.23 * weight) + (12.7 * height) - (6.8 * age + 66) - ((weight*0.7) * 5)) * 1.55
        rProtein = weight * 0.8
        rCarb = weight 
        rFat = weight * 0.2
    else:  # Maintain
        rCal = ((6.23 * weight) + (12.7 * height) - (6.8 * age + 66)) *1.55
        rProtein = weight 
        rCarb = weight * 1.2
        rFat = weight * 0.3 

    goal_and_info = {
        'Metric': "Goal and Info",
        'Goal': goal,
        'Height': height,
        'Weight': weight,
        'Age': age
    }
    save_to_files(goal_and_info)

    # Save Recommended as a separate entry
    recommended = {
        'Metric': "Recommended",
        'Calories': rCal,
        'Protein': rProtein,
        'Carbs': rCarb,
        'Fat': rFat
    }
    save_to_files(recommended)

    st.success("Your body info, goals, and recommended macros have been saved!")
    st.write(f"You entered: {weight} lbs, {height} inches, age {age}, goal: {goal}")
    st.write(f"Recommended Calories: {rCal:.0f} kcal")
    st.write(f"Protein: {rProtein:.1f} g, Carbs: {rCarb:.1f} g, Fat: {rFat:.1f} g")

st.subheader("🏅Macronutrient Daily Goals Survey")
with st.form("goal_form"):
    caloric_goals = st.slider("What is your caloric goal per day?",
                              min_value=0,
                              max_value=10000,
                              step=100)
    protein_goals = st.slider("What is your protein goal per day?",
                              min_value=0,
                              max_value=800,
                              step=10)
    carb_goals = st.slider("What is your carbohydrate goal per day?",
                           min_value=0,
                           max_value=1000,
                           step=10)
    fat_goals = st.slider("What is your total fat goal per day?",
                          min_value=0,
                          max_value=500,
                          step=5)
    submitted_goals_input = st.form_submit_button("Submit Goal Info")

if submitted_goals_input:
    new_goal = {
        "Metric": "Goal",
        "Calories": caloric_goals,
        "Protein": protein_goals,
        "Carbs": carb_goals,
        "Fat": fat_goals
    }
    save_to_files(new_goal)
    st.success("Your goal has been saved!")
    st.write(f"You entered: {caloric_goals} calories, {protein_goals} protein, {carb_goals} carbs, {fat_goals} fat")

st.subheader("🗓️Daily Macro Survey")
with st.form("daily_form"):
    caloric_input = st.number_input("How many calories do you eat in a day?", min_value=0)
    protein_input = st.number_input("How many grams of protein do you eat in a day?", min_value=0)
    carb_input = st.number_input("How many grams of carbs do you eat in a day?", min_value=0)
    fat_input = st.number_input("How many grams of fat do you eat in a day?", min_value=0)
    submitted_daily_input = st.form_submit_button("Submit Daily Info")

if submitted_daily_input:
    new_intake = {
        'Metric': "Intake",
        'Calories': caloric_input,
        'Protein': protein_input,
        'Carbs': carb_input,
        'Fat': fat_input,
    }
    save_to_files(new_intake)
    st.success("Your intake has been saved!")
    st.write(f"You entered: {caloric_input} calories, {protein_input} protein, {carb_input} carbs, {fat_input} fat")

st.write('---')

# DATA DISPLAY
st.divider()
st.header("Current Data in CSV")

if os.path.exists('data.csv') and os.path.getsize('data.csv') > 0:
    current_data_df = pd.read_csv('data.csv')
    st.dataframe(current_data_df)
else:
    st.warning("The 'data.csv' file is empty or does not exist yet.")
