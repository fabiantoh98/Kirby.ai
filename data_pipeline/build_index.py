import json
import os
from pathlib import Path
import glob

def load_json_files(directory):
    """Load all labeled_data_batch_{i}.json files from directory"""
    json_files = glob.glob(os.path.join(directory, "labeled_data_batch_*.json"))
    all_data = []
    for file in json_files:
        with open(file, 'r') as f:
            data = json.load(f)
            all_data.extend(data)
    return all_data

def build_forward_index(data):
    """Build a forward index mapping meal IDs to their full data"""
    forward_index = {}
    
    for item in data:
        meal_id = item['idMeal']
        
        # Initialize entry with core fields
        forward_index[meal_id] = {
            'strMeal': item['strMeal'],
            'strInstructions': item['strInstructions'],
            'strMealThumb': item['strMealThumb'],
            'ingredients': {},
            'health_benefit': item.get('health_benefit', {})
        }
        
        # Extract all ingredient/measure pairs
        for i in range(1, 21):
            ingredient = item.get(f'strIngredient{i}')
            measure = item.get(f'strMeasure{i}')
            
            # Only add if ingredient exists and isn't empty
            if ingredient and ingredient.strip():
                forward_index[meal_id]['ingredients'][ingredient] = measure

    return forward_index

def save_forward_index(index, output_dir):
    """Save the forward index to a JSON file"""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'forward_index.json')
    
    with open(output_path, 'w') as f:
        json.dump(index, f, indent=2)


def extract_scores_by_category(data):
    """Extract and organize scores for each health benefit category"""
    categories = {}
    
    for item in data:
        if 'health_benefit' not in item:
            continue
            
        confidence_scores = item['health_benefit'].get('confidence_score', {})
        meal_id = item['idMeal']
        
        for category, score_data in confidence_scores.items():
            if category not in categories:
                categories[category] = []
            
            categories[category].append({
                'id': meal_id,
                'score': score_data['score']
            })
    
    return categories

def sort_and_save_categories(categories, output_dir):
    """Sort meals by score for each category and save to files"""
    os.makedirs(output_dir, exist_ok=True)
    
    for category, meals in categories.items():
        # Sort by score in descending order
        sorted_meals = sorted(meals, key=lambda x: x['score'], reverse=True)
        
        # Create filename from category
        filename = f"{category.replace('_', '-')}.txt"
        filepath = os.path.join(output_dir, filename)
        
        # Write sorted meal IDs to file
        with open(filepath, 'w') as f:
            for meal in sorted_meals:
                f.write(f"{meal['id']}\t{meal['score']}\n")

def main():
    # Set up paths
    current_dir = Path(__file__).parent
    data_dir = current_dir
    output_dir = current_dir / 'health_indices'

    data = load_json_files(data_dir)

    # build forward index
    forward_index = build_forward_index(data)
    save_forward_index(forward_index, output_dir)
    
    # Load and process data
    categories = extract_scores_by_category(data)
    sort_and_save_categories(categories, output_dir)



if __name__ == "__main__":
    main()
