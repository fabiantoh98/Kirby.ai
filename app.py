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
        background-color: black;
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
    st.subheader("Top 5 Recipe")
    st.markdown("This page displays recipes along with details including image, meal name, explanation, instructions, and YouTube link.")

    # Load the JSON file from the data folder
    try:
        with open("data/small_data.json", "r") as f:
            recipes = json.load(f)
    except Exception as e:
        st.error(f"Error loading data/small_data.json: {e}")
        return

    # Loop over each recipe in the JSON file and display the details
    for rec in recipes:
        st.markdown("---")
        # Header with recipe name
        recipe_name = rec.get("strMeal", "No Recipe Name")
        st.header(recipe_name)
        with st.expander("Show Details"):

            # Create two columns: left for image, right for details
            col1, col2 = st.columns([1, 2])
            with col1:
                image_url = rec.get("strMealThumb")
                if image_url:
                    st.image(image_url, use_container_width=True)
                else:
                    st.text("No image available.")

            with col2:
                st.markdown(f"**Primary:** {rec.get('primary', 'N/A')}")
                st.markdown(f"**Confidence:** {rec.get('confidence', 'N/A')}")
                st.markdown(f"**Explanation:** {rec.get('exp', 'N/A')}")
                st.markdown(f"**Category:** {rec.get('strCategory', 'N/A')}")
                st.markdown(f"**Area:** {rec.get('strArea', 'N/A')}")
                st.markdown("**Instructions:**")
                st.write(rec.get("strInstructions", "N/A"))
                youtube_link = rec.get("strYoutube")
                if youtube_link:
                    st.markdown(f"**YouTube Link:** {youtube_link}")
                    st.video(youtube_link)
                else:
                    st.text("No YouTube link available.")

    st.markdown("---")
    st.success("End of recipes.")

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
    else:
        health_goal_page()

if __name__ == "__main__":
    main()

