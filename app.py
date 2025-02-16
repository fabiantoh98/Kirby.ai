import streamlit as st

from PIL import Image
import pandas as pd
import numpy as np
from get_openai_response import get_recipes_from_image, get_meals_from_response
from health_matching import find_matching_recipes
import json
import random
import time
from datetime import datetime

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
    .stMetric, .stMetric * {
      color: #000000 !important;
    }
    .stTable, .stTable * {
      color: #000000 !important;
    }
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
    stTextArea textarea,
    .stNumberInput input {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    /* Ensure form labels are black */
    .stForm label,
    .stForm span {
        color: #000000 !important;
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
    if "token_balance" not in st.session_state:
        st.session_state.token_balance = 100  # starting tokens
    if "transactions" not in st.session_state:
        st.session_state.transactions = [{
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Description": "Initial Balance",
            "Tokens": 100,
            "Balance": 100
        }]
    if 'contributions' not in st.session_state:
        st.session_state.contributions = []

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
    st.button("Back to Health Goals", key="back_to_goals")
    st.success("End of recipes.")

# ----- TOKEN WALLET PAGE -----
def token_wallet_page():
    st.title("Token Wallet")
    st.markdown("Welcome to your token wallet! Here you can view your current token balance, review recent transactions, and purchase additional tokens.")

    # Ensure token balance and transactions are initialized
    if "token_balance" not in st.session_state:
        st.session_state.token_balance = 100  # starting tokens
    if "transactions" not in st.session_state:
        st.session_state.transactions = [{
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Description": "Initial Balance",
            "Tokens": 100,
            "Balance": 100
        }]

    # Display current token balance
    st.metric("Current Token Balance", st.session_state.token_balance)

    st.markdown("### Recent Transactions")
    df = pd.DataFrame(st.session_state.transactions)
    st.table(df)

    st.markdown("### Buy More Tokens")
    tokens_to_buy = st.number_input("Enter number of tokens to buy:", min_value=1, step=1, value=10)
    if st.button("Buy Tokens"):
        # Update the token balance
        st.session_state.token_balance += tokens_to_buy

        # Create a new transaction record
        new_txn = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Description": "Purchased Tokens",
            "Tokens": tokens_to_buy,
            "Balance": st.session_state.token_balance
        }
        st.session_state.transactions.append(new_txn)

        # Debug output: show new transaction and full list
        st.write("New Transaction:", new_txn)
        st.write("All Transactions:", st.session_state.transactions)
        # Instead of forcing an immediate rerun, use a small delay or ask the user to refresh
        time.sleep(0.2)
        st.experimental_rerun()  # Try commenting this line out to see if the table updates correctly

def contribution_page():
    st.title("Contribute Your Recipe")
    st.markdown(
        """
        Help improve our AI model by contributing your favorite recipes. The more your recipe is recommended by the community,
        the more tokens you'll receive as an appreciation bonus!
        """
    )
    
    # Recipe contribution form
    with st.form("contribution_form", clear_on_submit=True):
        recipe_name = st.text_input("Recipe Name")
        recipe_description = st.text_area("Recipe Description / Instructions", height=150)
        submitted = st.form_submit_button("Submit Recipe")
        
    if submitted:
        recommended_count = random.randint(0, 20)
        base_tokens = 10  # base tokens for contributing a recipe
        bonus_tokens = int(recommended_count) * 2  # bonus per recommendation
        total_tokens_awarded = base_tokens + bonus_tokens
        
        st.session_state.token_balance += total_tokens_awarded
        
        # Record the contribution (simulated database)
        new_contribution = {
            "Recipe Name": recipe_name,
            "Recommendations": recommended_count,
            "Awarded Tokens": total_tokens_awarded,
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.contributions.append(new_contribution)
        
        st.success(f"Thank you for contributing! You've been awarded {total_tokens_awarded} tokens.")
        st.experimental_rerun()
    
    st.markdown("### Your Contributions")
    if st.session_state.contributions:
        df = pd.DataFrame(st.session_state.contributions)
        st.table(df)
    else:
        st.info("No contributions yet. Submit a recipe to see it here!")



def main():
    # Initialize session state
    initialize_session_state()

    # Toaster tips
    tips = [
        "Did you get your healthy meal today?",
        "Remember to stay hydrated!",
        "A balanced diet is a key to a healthy life.",
        "Don't forget to include fruits and vegetables in your meals.",
        "Healthy eating is a journey, not a destination.",
        "Small changes can make a big difference in your health.",
        "Eat a variety of foods to get all the nutrients you need.",
        "Moderation is the key to a healthy diet.",
        "Enjoy your food, but eat less.",
        "Make half your plate fruits and vegetables."
    ]

    st.toast(random.choice(tips))

    with st.container():
        st.sidebar.title("Navigation")
        previous_page = st.session_state.get('current_page', 'Health Goals')
        selected_page = st.sidebar.radio(
            "Go to",
            ["Health Goals", "Top Recipes", "Token", "Contribution"]
        )
        
        # Track page changes
        if selected_page != previous_page:
            st.session_state['current_page'] = selected_page
            print(f"Page changed from {previous_page} to {selected_page}")
            print(f"Current similarity scores: {st.session_state.similarity_scores}")

        st.html("""
            <div style="display: flex; align-items: center; gap: 10px;">
                <img src="https://i.ibb.co/hx8VhjyR/round-kirchin.png" alt="Kirchin" width="100" height="100">
                <h1 style="margin: 10px; font-size: 48px;">Kirby.AI</h1>
            </div>
        """)
        st.markdown("""
            #### Welcome to **Kirby.AI**: The recipe recommender that makes your grandma happy :balloon: ####
        """)

                
        # Page routing based on session state
        if st.session_state.clicked or selected_page == "Top Recipes":
            top_recipe_page()
            st.session_state.clicked = False
        if st.session_state.clicked or selected_page == "Token":
            token_wallet_page()
            st.session_state.clicked = False
        if st.session_state.clicked or selected_page == "Contribution":
            contribution_page()
            st.session_state.clicked = False
        else:
            health_goal_page()



if __name__ == "__main__":
    main()