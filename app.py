import streamlit as st

from PIL import Image
import pandas as pd
import numpy as np
from get_openai_response import get_recipes_from_image


# ----- PAGE CONFIG & STYLES -----
st.set_page_config(
    page_title="Kirby.AI",
    page_icon="🌆",
    layout="wide"
)
# Inject a bit of CSS to style metric cards, titles, etc.
st.markdown(
    """
    <style>
    .stContainer {
        background-color: #F9F9F9;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #fff;
        border-radius: 6px;
        padding: 10px 15px;
        text-align: center;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    /* Sidebar style tweaks */
    section[data-testid="stSidebar"] {

        background-color: #bab6b6;
    }
    section[data-testid="stSidebar"] .css-1d391kg {
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

health_goals = {
    "Boost Metabolism": "Optimize your metabolism and support healthy weight management with metabolism-boosting dishes.",
    "Boost Energy": "Recharge your body with nutrient-rich meals designed to enhance vitality and combat fatigue.",
    "Enhance Focus": "Sharpen your mental clarity and concentration with brain-boosting ingredients.",
    "Improve Immunity": "Strengthen your body's natural defenses with immune-boosting ingredients and nourishing recipes.",
    "Improve Mobility": "Enhance joint flexibility and bone health with meals designed to support overall mobility.",
    "Detox": "Assist your body's natural detoxification processes with cleansing and purifying foods.",
    "Enhance Mood": "Elevate your mood and promote emotional well-being with mood-enhancing ingredients.",
    "Aid Sleep Quality": "Improve your sleep quality and ensure restful nights with calming and sleep-inducing ingredients."
}

def initialize_session_state():
    if 'clicked' not in st.session_state:
        st.session_state.clicked = False
    if 'selected_goal' not in st.session_state:
        st.session_state.selected_goal = None
    if 'goal_description' not in st.session_state:
        st.session_state.goal_description = None

def go_to_recipe_page(goal):
    st.session_state.clicked = True
    st.session_state.selected_goal = goal
    st.session_state.goal_description = health_goals[goal]

def health_goal_page():
    st.subheader("Select Your Health Goal:")
    
    for goal, description in health_goals.items():
            with st.expander(goal):
                st.write(description)
                st.button(f"Select {goal}", key=f"btn_{goal}", 
                         on_click=go_to_recipe_page, args=(goal,))


    # Image upload section
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = np.array(Image.open(uploaded_file))
        st.image(image, caption='Uploaded Image.', use_container_width=True)
        st.write("")
        with st.spinner("Extracting text..."):
            response = get_recipes_from_image(image)
        if response.strip():
            st.text_area("Extracted Text", response, height=200)
        else:
            st.write("No text found in the image.")

def top_recipe_page():
    st.subheader("Top 5 Recipes")
    
    # Display selected health goal information
    if st.session_state.selected_goal:
        st.write("**Selected Health Goal:**", st.session_state.selected_goal)
        st.write("**Goal Description:**", st.session_state.goal_description)
        
        # Add a button to go back to health goals
        if st.button("Choose Different Goal"):
            st.session_state.clicked = False

def main():

    # Initialize session state
    initialize_session_state()
    
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio(
        "Go to",
        ["Health Goals", "Top Recipes"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.write("**User:** John Doe")
    st.sidebar.write("**Version:** 0.0.1")
    if st.sidebar.button("Logout"):
        st.sidebar.write("You have logged out.")

    st.title("Kirby.AI")
    st.markdown("""
        Welcome to **Kirby.AI**: The best foody recommender in the market.
    """)
    
    # Page routing based on session state
    if st.session_state.clicked or selected_page == "Top Recipes":
        top_recipe_page()
        st.session_state.clicked = False
    else:
        health_goal_page()

if __name__ == "__main__":
    main()