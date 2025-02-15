import streamlit as st
import pytesseract
from PIL import Image
from google import genai
from google.genai import types
import pandas as pd
import numpy as np

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
def main():
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio(
        "Go to",
        ["Page 1", "Page 2"]
    )
    st.sidebar.markdown("---")
    st.sidebar.write("**User:** John Doe")
    st.sidebar.write("**Version:** 0.0.1")
    if st.sidebar.button("Logout"):
        st.sidebar.write("You have logged out.")
    st.title("Kirby.AI")
    st.markdown(
        """
        Welcome to the **Kirby.AI**: THe best foody recommender in the market.
        """
    )
    if selected_page == "Page 1":
        page_1()
    elif selected_page == "Page 2":
        page_2()
def page_1():
    st.subheader("Food Recommender")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = np.array(Image.open(uploaded_file))
        st.image(image, caption='Uploaded Image.', use_container_width=True)
        st.write("")
        with st.spinner("Extracting text..."):
            
            @st.cache_data
            def load_ingredients():
                return pd.read_json('ingredients.json')
            
            @st.cache_data
            def load_meals():
                return pd.read_json('big_data.json')
            
            client = genai.Client(api_key="")
            text = pytesseract.image_to_string(image)
            ingredients = load_ingredients()
            meals = load_meals()
            response = client.models.generate_content(
                model="gemini-2.0-flash", contents=[text, ingredients.to_string(), meals.to_string(), "Obtain the food items from the image then cross reference with the ingredients list and filter only the food items that exist in the ingredients list and get the ingredient list name. After that, obtain the strMeal's that matches the ingredients best and return it. Then returned object should just contain the strMeals's + included ingredients + excluded ingredients and nothing else. If none then say none."]
            )
            print(response.text)
        if response.text.strip():
            # ingredients = load_ingredients()
            # st.write(ingredients)
            st.text_area("Extracted Text", response.text, height=200)
        else:
            st.write("No text found in the image.")


    
def page_2():
    st.subheader("Display")


if __name__ == "__main__":
    main()