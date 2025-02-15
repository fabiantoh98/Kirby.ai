import streamlit as st
import pytesseract
from PIL import Image
from google import genai
from google.genai import types
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
    "Reduce Heatiness" : '''
        A therapeutic approach aimed to remove excessive heat within the body.
        Some common causes of heatiness includes exposure to hot weather, inflammatory conditions,
        emotional imbalances (stress, anger) and overconsumption of spicy and warming foods.
        ''',
    "Improve Immunity" : "to improve your immunity"
}

top_5_recipe = {
    "Chickem Rice": "",
    "Ceasar Salad": ""
}

def main():
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
    st.title("Kitchen Co-pilot Medicinal Cooking Recipes")
    st.markdown(
        """
        Welcome to the **Kirby.AI**: The best foody recommender in the market.
        """
    )
    if selected_page == "Health Goals":
        health_goal_page()
    elif selected_page == "Top Recipes":
        top_recipe_page()

def health_goal_page():
    st.subheader("Food Recommender")

    st.subheader("Select Your Health Goal: ")
    # Load each of the options
    for goal, description in health_goals.items():
        with st.expander(goal):
            st.write(description)
            if st.button(goal):
                top_recipe_page()



    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = np.array(Image.open(uploaded_file))
        st.image(image, caption='Uploaded Image.', use_container_width=True)
        st.write("")
        with st.spinner("Extracting text..."):
            response = get_recipes_from_image(image)
        if response.strip():
            # ingredients = load_ingredients()
            # st.write(ingredients)
            st.text_area("Extracted Text", response, height=200)
        else:
            st.write("No text found in the image.")


    
def top_recipe_page():
    st.subheader("Display")


if __name__ == "__main__":
    main()



#  "Obtain the food items from the image then cross reference with the ingredients list and filter only the food items that exist in the ingredients list and get the ingredient list name. After that, obtain the strMeal's that matches the ingredients best and return it. Then returned object should just contain the strMeals's + included ingredients + excluded ingredients and nothing else. If none then say none."