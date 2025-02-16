import streamlit as st

from PIL import Image
import pandas as pd
import numpy as np
from get_openai_response import get_recipes_from_image, get_meals_from_response
from health_matching import find_matching_recipes
import json
import random
import time

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

    .stButton:hover {
    color: var(--primary-color-black);
    font-weight: bold;
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
    if 'ingredient_list' not in st.session_state:
        st.session_state.ingredient_list = None

def go_to_recipe_page(goal):
    st.balloons()
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
    uploaded_file = st.file_uploader("Choose a receipt...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.balloons()
        image = np.array(Image.open(uploaded_file))
        st.image(image, caption='Uploaded Image.', use_container_width=False)
        st.write("")
        with st.spinner("Extracting text..."):
            response = get_recipes_from_image(uploaded_file)
            st.session_state.ingredient_list = response
            similarity_scores = get_meals_from_response(json.loads(response).get("ingredients", []))
            print("Setting similarity scores:", similarity_scores)
            st.session_state['similarity_scores'] = similarity_scores
            print("Similarity scores after setting:", st.session_state.similarity_scores)
            # st.write("Similarity Scores:", similarity_scores["similarity_scores"])
            if response.strip():
                st.subheader("Extracted Ingredients:")
                # json.loads(response
                ingredients = json.loads(response).get("ingredients", [])
                df_ingredients = pd.DataFrame(ingredients, columns=["Ingredients"])
                df_ingredients.index += 1
                st.dataframe(df_ingredients, use_container_width=True)

            else:
                st.write("No text found in the image.")
            st.subheader("Recommended Foods:")
            best_meals = []
            for _, v in similarity_scores["similarity_scores"]:
                best_meals.append({"Meal Name": v["name"], "What you have": v["intersection"], "What you don't have": v["exception"]})

            meals_df = pd.DataFrame(best_meals, columns=["Meal Name", "What you have", "What you don't have"])
            meals_df.index += 1
            st.dataframe(meals_df, use_container_width=True)


def top_recipe_page():
    print("Entering top_recipe_page with similarity scores:", st.session_state.similarity_scores)
    st.button("Back to Health Goals", key="back_to_goals")
    st.subheader("Top 5 Recipe")
    st.markdown("This page displays *recipes* along with details including images, meal names, explanatios, instructions, and YouTube links.")
    # st.write("Current Similarity Scores:", st.session_state.similarity_scores)
    if st.session_state.similarity_scores is not None:
        st.info("See checklists for ingredients you have and don't have from your photo.")
    
    goal = st.session_state.selected_goal
    st.markdown(f'''
        Top 5 Recipes for _{goal}_:''')
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

        reciept_ingredient_list = st.session_state.ingredient_list.lower() if st.session_state.ingredient_list else []
        for k,v in ingredients_dict.items():
            ingredients_list.append({"Ingredient": k, "Quantity": v, "checklist": k.lower() in reciept_ingredient_list})
        df_ingredients = pd.DataFrame(ingredients_list)
        df_ingredients.index += 1 
        
        with col2:
            with st.expander("Show Details"):
                st.markdown(f"**Health Goal:** {goal}")
                st.markdown(f"**Health Score:** {rec.get('health_score', 'N/A')}")
                st.markdown(f"**Explanation:** {rec.get('reason', 'N/A')}")
                
                st.dataframe(df_ingredients, use_container_width=True)

                st.markdown(f"**Health Score:** {rec.get('health_score', 'N/A')}")
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

    # Toaster tips
    tips = [
        "Nourish Your Soul: Cultivating Wellness.",
        "Embrace Wholeness: Elevating Wellness.",
        "Health in Harmony: Discover Wellness.",
        "Pure Vitality: Nurturing Wellness.",
        "Flourish Inside Out: Achieving Wellness.",
        "Wellness Journey: Transforming Lives.",
        "Radiant Health: Uniting Flavor and Wellness.",
        "One Thoughtful Medicinal Meal at a Time.",
        "One Medicinal Cuisine at a Time.",
        "One Medicinal Meal at a Time.",
        "One Healing Dish at a Time.",
        "One Nourishing Plate at a Time.",
        "One Medicinal Bite at a Time.",
        "One Wholesome Meal at a Time."
    ]

    st.toast(random.choice(tips))

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

        st.html("""
            <div style="display: flex; align-items: center; gap: 10px;">
                <img src="https://i.ibb.co/hx8VhjyR/round-kirchin.png" alt="Kirchin" width="100" height="100">
                <h1 style="margin: 10px; font-size: 48px;">Kirchen.AI</h1>
            </div>
        """)
        st.markdown("""
            #### Welcome to **Kirchen.AI**: The recipe recommender that makes your grandma happy :balloon: ####
        """)

                
        # Page routing based on session state
        if st.session_state.clicked or selected_page == "Top Recipes":
            top_recipe_page()
            st.session_state.clicked = False
        else:
            health_goal_page()



if __name__ == "__main__":
    main()