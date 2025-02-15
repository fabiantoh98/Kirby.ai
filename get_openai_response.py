from openai import OpenAI
import pytesseract
import pandas as pd
import os


def load_ingredients():
    return pd.read_json("ingredients.json").to_string()

def get_recipes_from_image(image):

    text = pytesseract.image_to_string(image)
    ingredients = load_ingredients()
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )


    response = client.chat.completions.create(
    model="gpt-4o",
    messages = [
        {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "Given the food items in here: {text}, cross reference/map it with the ingredients in here: {ingredients} and return the corresponding ingredients list meal indivually."
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