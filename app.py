import streamlit as st

from PIL import Image
import pandas as pd
import numpy as np
from get_openai_response import get_recipes_from_image, get_meals_from_response
from health_matching import find_matching_recipes
import json

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
    /* Primary Colors */
    :root {
    --primary-color-white: #FFFFFF;
    --primary-color-black: #000000;
    }

    /* Secondary Colors */
    :root {
    --secondary-color-spearmint: #63D297;
    --secondary-color-kirby-pink: #D74894;
    }

    /* Accent Colors */
    :root {
    --accent-color-dark-grey: #A9A9A9;
    --accent-color-light-grey: #D4D4D4;
    }

    .stApp {
    background-color: var(--primary-color-white);
    color: var(--primary-color-black);
    }

    .stButton {
    background-color: RGBA(0,0,0,0);
    color: var(--primary-color-black);
    border: none;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
    }

    .stButton > button {
    background-color: var(--accent-color-light-grey);
    }

    .stTextInput {
    width: 100%;
    padding: 10px;
    margin-bottom: 20px;
    border: 1px solid var(--accent-color-light-grey);
    border-radius: 5px;
    box-sizing: border-box;
    }

    .stSelectbox {
    width: 100%;
    padding: 10px;
    margin-bottom: 20px;
    border: 1px solid var(--accent-color-light-grey);
    border-radius: 5px;
    box-sizing: border-box;
    }

    .stRadio {
    margin-bottom: 20px;
    }

    .stCheckbox {
    margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

health_goals = {
    "Boost Energy": "Recharge your body with nutrient-rich meals designed to enhance vitality and combat fatigue.",
    "Boost Metabolism": "Optimize your metabolism and support healthy weight management.",
    "Enhance Focus": "Sharpen your mental clarity and concentration with brain-boosting ingredients.",
    "Improve Immunity": "Strengthen your body's natural defenses with immune-boosting ingredients and nourishing recipes.",
    "Improve Mobility": "Enhance your joint flexibility and bone health with meals designed to support overall mobility.",
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
    if 'similarity_scores' not in st.session_state:
        st.session_state.similarity_scores = None

def go_to_recipe_page(goal):
    st.session_state.clicked = True
    st.session_state.selected_goal = goal
    st.session_state.goal_description = health_goals[goal]

def health_goal_page():
    with st.container():
        st.subheader("Select Your Health Goal:")
        col1, col2, col3 = st.columns(3)
        for i, (goal, description) in enumerate(health_goals.items()):
            with eval(f"col{i % 3 + 1}").expander(goal):
                print(f"Current similarity scores in health goal expander: {st.session_state.similarity_scores}")
                st.write(description)
                st.button(f"Select {goal}", key=f"btn_{goal}", 
                        on_click=go_to_recipe_page, args=(goal,))

        with col3.expander(" ... "):
            st.write("""... more to come.""")

    # Image upload section
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = np.array(Image.open(uploaded_file))
        st.image(image, caption='Uploaded Image.', use_container_width=False)
        st.write("")
        with st.spinner("Extracting text..."):
            response = get_recipes_from_image(uploaded_file)
            similarity_scores = get_meals_from_response(json.loads(response).get("ingredients", []))
            print("Setting similarity scores:", similarity_scores)
            st.session_state['similarity_scores'] = similarity_scores
            print("Similarity scores after setting:", st.session_state.similarity_scores)
            st.write("Similarity Scores:", similarity_scores)
        if response.strip():
            st.write("Extracted Ingredients", json.loads(response))
        else:
            st.write("No text found in the image.")

def top_recipe_page():
    print("Entering top_recipe_page with similarity scores:", st.session_state.similarity_scores)
    st.subheader("Top 5 Recipe")
    st.markdown("This page displays recipes along with details including image, meal name, explanation, instructions, and YouTube link.")
    st.write("Current Similarity Scores:", st.session_state.similarity_scores)
    
    goal = st.session_state.selected_goal
    recipes = find_matching_recipes([st.session_state.selected_goal]).get(goal)

    # Load the JSON file from the data folder
    # try:
    #     with open("data/small_data.json", "r") as f:
    #         recipes = json.load(f)
    # except Exception as e:
    #     st.error(f"Error loading data/small_data.json: {e}")
    #     return

    # Loop over each recipe in the JSON file and display the details
    for rec in recipes:
        st.markdown("---")
        # Header with recipe name
        recipe_name = rec.get("strMeal", "No Recipe Name")
        st.header(recipe_name)
        

        # Create two columns: left for image, right for details
        col1, col2 = st.columns([1, 2])
        with col1:
            image_url = rec.get("strMealThumb")
            if image_url:
                st.image(image_url, width=400)
            else:
                st.text("No image available.")
        ingredients_dict = rec.get('ingredients', 'N/A')
        ingredients_list = []
        for k,v in ingredients_dict.items():
            ingredients_list.append({"Ingredient": k, "Quantity": v})
        df_ingredients = pd.DataFrame(ingredients_list)
        df_ingredients.index += 1 
        
        with col2:
            with st.expander("Show Details"):
                st.markdown(f"**Health Goal:** {goal}")
                st.markdown(f"**Health Score:** {rec.get('health_score', 'N/A')}")
                st.markdown(f"**Explanation:** {rec.get('reason', 'N/A')}")
                
                st.dataframe(df_ingredients, use_container_width=True)

                st.markdown(f"**Health Score:** {rec.get('health_score', 'N/A')}")
                # st.markdown(f"**Category:** {rec.get('strCategory', 'N/A')}")
                # st.markdown(f"**Area:** {rec.get('strArea', 'N/A')}")
                st.markdown("**Instructions:**")
                st.write(rec.get("strInstructions", "N/A"))
                # youtube_link = rec.get("strYoutube")
                # if youtube_link:
                #     st.markdown(f"**YouTube Link:** {youtube_link}")
                #     st.video(youtube_link)
                # else:
                #     st.text("No YouTube link available.")

    st.markdown("---")
    st.button("Back to Health Goals", key="back_to_goals")
    st.success("End of recipes.")

def main():
    # Initialize session state
    initialize_session_state()
    
    with st.container():
        st.sidebar.title("Navigation")
        previous_page = st.session_state.get('current_page', 'Health Goals')
        selected_page = st.sidebar.radio(
            "Go to",
            ["Health Goals", "Top Recipes"]
        )
        
        # Track page changes
        if selected_page != previous_page:
            st.session_state['current_page'] = selected_page
            print(f"Page changed from {previous_page} to {selected_page}")
            print(f"Current similarity scores: {st.session_state.similarity_scores}")

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