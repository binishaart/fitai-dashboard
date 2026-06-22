import streamlit as st
import json

st.set_page_config(
    page_title="Workout Summary",
    page_icon="🏋️",
    layout="wide"
)

st.title("🏋️ Smart Gym Assistant Report")

with open("workout_data.json", "r") as f:
    data = json.load(f)

col1, col2 = st.columns(2)

with col1:

    st.metric("Exercise", data["exercise"].upper())

    st.metric("Total Reps", data["reps"])

    st.metric("Workout Time", f'{data["workout_time"]} sec')

with col2:

    st.metric("Heart Rate", f'{data["heart_rate"]} BPM')

    st.metric("Calories Burned", data["calories"])

    st.metric("Performance Score", f'{data["score"]}%')

st.divider()

st.subheader("🤖 AI Recommendation")

st.success(data["recommendation"])

if data["score"] >= 90:
    st.balloons()