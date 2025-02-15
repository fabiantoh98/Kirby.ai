from typing import List, Dict
import json

def find_matching_recipes(health_options: List[str]):
    result_dict = {}
    for option in health_options:
        health_option_str = option.lower().replace(" ", "-")
        health_option_underline = option.lower().replace(" ", "_")
        # Read health indices file
        with open(f'data_pipeline/health_indices/{health_option_str}.txt', 'r') as f:
            lines = f.readlines()
            
        # Parse top 5 meal IDs and scores
        top_meals = []
        for line in lines[:5]:
            meal_id, score = line.strip().split('\t')
            top_meals.append({
                'id': meal_id,
                'score': float(score)
            })
            
        # Look up meal details in forward index
        with open('data_pipeline/health_indices/forward_index.json', 'r') as f:
            forward_index = json.load(f)
            
        # Get meal details for top 5
        meal_details = []
        for meal in top_meals:
            meal_id = meal['id']
            if meal_id in forward_index:
                details = forward_index[meal_id]
                details['health_score'] = meal['score']
                details["id"] = meal_id
                details['reason'] = details['health_benefit']['confidence_score'][health_option_underline]["explanation"]
                meal_details.append(details)
        result_dict[option] = meal_details
    return result_dict

print(json.dumps(find_matching_recipes(["Detox", "Improve Mobility"])))