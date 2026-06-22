import streamlit as st

st.set_page_config(
    page_title="AI Dietician",
    page_icon="🥗"
)
st.markdown(
    '<a href="http://localhost:8501" target="_self">🏠 Back to Dashboard</a>',
    unsafe_allow_html=True
)
st.title("🥗 AI Dietician & Calorie Coach")

if "step" not in st.session_state:
    st.session_state.step = 1

if "weight" not in st.session_state:
    st.session_state.weight = None

if "height" not in st.session_state:
    st.session_state.height = None

if "goal" not in st.session_state:
    st.session_state.goal = None


# STEP 1
if st.session_state.step == 1:

    weight = st.number_input(
        "Enter Weight (kg)",
        min_value=1.0
    )

    if st.button("Next"):

        st.session_state.weight = weight
        st.session_state.step = 2
        st.rerun()


# STEP 2
elif st.session_state.step == 2:

    height = st.number_input(
        "Enter Height (cm)",
        min_value=50.0
    )

    if st.button("Next"):

        st.session_state.height = height
        st.session_state.step = 3
        st.rerun()


# STEP 3
elif st.session_state.step == 3:

    goal = st.selectbox(
        "Select Goal",
        [
            "Weight Loss",
            "Weight Gain",
            "Maintain"
        ]
    )

    if st.button("Generate Plan"):

        st.session_state.goal = goal
        st.session_state.step = 4
        st.rerun()


# STEP 4
elif st.session_state.step == 4:

    weight = st.session_state.weight
    height = st.session_state.height / 100

    bmi = weight / (height * height)

    if bmi < 18.5:

        diet = "Rice Bowl Diet"

        ingredients = [
            "Rice",
            "Milk",
            "Banana",
            "Peanut Butter",
            "Almonds"
        ]

    elif bmi > 25:

        diet = "Oats Protein Diet"

        ingredients = [
            "Oats",
            "Eggs",
            "Paneer",
            "Vegetables",
            "Fruits"
        ]

    else:

        diet = "Balanced Plate Diet"

        ingredients = [
            "Rice",
            "Milk",
            "Eggs",
            "Fruits",
            "Vegetables",
            "Nuts"
        ]

    st.success(f"BMI: {bmi:.2f}")

    st.write(f"### Diet: {diet}")

    st.write("### Ingredients List")

    for item in ingredients:
        st.write(f"• {item}")

    if st.button("Start Again"):

        st.session_state.step = 1
        st.rerun()