import streamlit as st
import pytesseract
from PIL import Image

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
            text = pytesseract.image_to_string(image)
        if text.strip():
            st.text_area("Extracted Text", text, height=200)
        else:
            st.write("No text found in the image.")


    
def page_2():
    st.subheader("Display")


if __name__ == "__main__":
    main()