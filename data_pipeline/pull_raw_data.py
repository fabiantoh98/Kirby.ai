import requests
import json

# Call TheMealDB API to get meal categories
response = requests.get('https://www.themealdb.com/api/json/v1/1/categories.php')

# Parse response as JSON
categories_data = response.json()

total_receit_num = 0
recipe_results = []
for cat in categories_data["categories"]:
    cat_str = cat["strCategory"]
    response = requests.get(f'https://www.themealdb.com/api/json/v1/1/filter.php?c={cat_str}')
    cat_recipes = response.json()
    for recipe in cat_recipes["meals"]:
        meal_id = recipe["idMeal"]
        recipe_detail = requests.get(f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}')
        total_receit_num+=1
        recipe_results.append(recipe_detail.json())
with open("big_data.json", 'w') as f:   
    json.dump(recipe_results, f)