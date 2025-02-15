from openai import OpenAI
# import pytesseract
import pandas as pd
import os
from google import genai

from PIL import Image
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

def load_ingredients():
    return pd.read_json("ingredients.json").to_string()


def extract_ingredients_from_image(image_path):
    client = genai.Client(api_key=gemini_api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=[Image.open(image_path), "What foods are in here, give me a list in this format"]
    )
    print(response.text)
    return response.text
    

def get_recipes_from_image(image_path):

    # text = pytesseract.image_to_string(image_path)
    # print(text)
    text = extract_ingredients_from_image(image_path)
    ingredients = load_ingredients()
    client = OpenAI(
        api_key = openai_api_key
    )
    prompt = f"""
    You are an AI assistant helping a user extract ingredients from an image and cross-reference them with a given list of ingredients. 
    Given the food items in here: {text}, cross-reference/map them with the ingredients in here: {ingredients} and return the corresponding ingredients list. 
    The words don't have to be exactly the same, but you should return a list of ingredients that only exist in the given list.
    """


    response = client.chat.completions.create(
    model="gpt-4o",
    messages = [
        {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt
                }
            ]
            },
            {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "You are an AI assistant helping a user extract the ingredients from an image and cross-referencing it with the ingredients list to return the corresponding ingredients list meal from the json."
                }
            ]
            }
        ],
        response_format = {
        "type": "json_schema",
        "json_schema": {
        "name": "ingredients_list",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
            "ingredients": {
                "type": "array",
                "description": "An array of single word ingredients.",
                "items": {
                "type": "string",
                "description": "A single word representing an ingredient."
                }
            }
            },
            "required": [
            "ingredients"
            ],
            "additionalProperties": False
        }
        }
    },
    temperature=1,
    max_completion_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return response.choices[0].message.content

def get_meals_from_response(ingredients):
    #convert ingredients to lowercase
    ingredients = [ingredient.lower() for ingredient in ingredients]
    meals = pd.read_json('data/big_data.json')
    extracted_meals = []
    for i in range(50):
        extracted_meal_ingredients = []
        meal = meals.iloc[i, 0][0]
        for i in range(20):
            # print(meal[f'strIngredient{i+1}'].lower())
            extracted_meal_ingredients.append(meal[f'strIngredient{i+1}'].lower() if meal[f'strIngredient{i+1}'] else "")
        extracted_meals.append({"id": meal["idMeal"], "ingredients": extracted_meal_ingredients})
    similarity_scores = {}
    for meal_ingredients in extracted_meals:
        # intersection = set()
        # for ingredient in ingredients:
        #     for meal_ingredient in meal_ingredients:
        #         if ingredient in meal_ingredient or meal_ingredient in ingredient:
        #             intersection.add(meal_ingredient)
        intersection = set(meal_ingredients['ingredients']).intersection(set(ingredients))
        similarity_scores[meal_ingredients['id']] = {"intersection": list(intersection), "exception": list(set(ingredients) - intersection), "similarity_score": len(intersection) / len(ingredients), "total_overlap_amount": len(intersection)}
        
    
    # sort the similarity scores
    sorted_similarity_scores = sorted(similarity_scores.items(), key=lambda x: x[1]["similarity_score"], reverse=True)

    # return {"meals": extracted_meals, "ingredients": ingredients, "similarity_scores": sorted_similarity_scores}
    return {"similarity_scores": sorted_similarity_scores[:5]}

