import json

from openai import OpenAI
from pydantic import BaseModel

class ScoreExplain(BaseModel):
  score: float
  explanation: str

class ConfidenceScore(BaseModel):
  boost_metabolism: ScoreExplain
  boost_energy: ScoreExplain
  enhance_focus: ScoreExplain
  improve_immunity: ScoreExplain
  improve_mobility: ScoreExplain
  detox: ScoreExplain
  enhance_mood: ScoreExplain
  aid_sleep_quality: ScoreExplain

class Result(BaseModel):
    health_benefit: str
    confidence_score: ConfidenceScore
    

health_options = """
Boost Metabolism: Optimize your metabolism and support healthy weight management with metabolism-boosting dishes.
Boost Energy: Recharge your body with nutrient-rich meals designed to enhance vitality and combat fatigue.
Enhance Focus: Sharpen your mental clarity and concentration with brain-boosting ingredients.
Improve Immunity: Strengthen your body's natural defenses with immune-boosting ingredients and nourishing recipes
Improve mobility: Enhance joint flexibility and bone health with meals designed to support overall mobility.
Detox: Assist your body's natural detoxification processes with cleansing and purifying foods.
Enhance Mood: Elevate your mood and promote emotional well-being with mood-enhancing ingredients.
Aid Sleep Quality: Improve your sleep quality and ensure restful nights with calming and sleep-inducing ingredients.
"""

system_prompt = """
You are a TCM nutritionist and an expert in Chinese medicinal cruisine.
"""

client = OpenAI(api_key="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")

# Read input JSON file
with open('sampled_data_2.json', 'r') as f:
    data = json.load(f)

labeled_data = []
batch_num = 18
total_num = 0

# Iterate through each recipe
for recipe in data:
    if "meals" in recipe:
      recipe = recipe["meals"][0]
    # Extract recipe details
    recipe_str = json.dumps(recipe, indent=2)
  
    user_prompt_template = f"""
    I have a recipe and a list of potential health benefits. 
    Please analyze the recipe's ingredients and instructions to determine the health benefit it provides.
    Focus on the traditional chinese medicine benefits of the ingredients. Think about the relative quantity of the ingredients.
    Give a score for all the Potential Health Benefits, and choose the highest-scored one as the primary health benefit. Give an explanation to each score.
    Make the explanation more detailed for the primary health_benefit.

    Recipe Details:
    {recipe_str}

    Potential Health Benefits:
    {health_options}

    Task:
    1. Analyze the ingredients and their relative quantities. Understand how it will bring about health benefits from a TCM perspective.
    2. Provide a score for all the potential health benefit based on the analysis. Choose the highest-scored one as the primary health benefit.
    3. Provide a brief explanation of why each health benefit has the specific score, considering the ingredients and cooking method.
    """
    
    # Call OpenAI API to get health benefit label
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user", 
                "content": user_prompt_template
            }
        ],
        response_format=Result
    )
    
    # Get label from completion
    label = completion.choices[0].message.parsed
    
    # Add label to recipe
    recipe['health_benefit'] = label.model_dump()
    labeled_data.append(recipe)
    total_num += 1
    print(f"-- {total_num}")

    # Write batch of 10 items to file
    if len(labeled_data) == 10:
        batch_num += 1
        with open(f'labeled_data_batch_{batch_num}.json', 'w') as f:
            json.dump(labeled_data, f, indent=2)
        labeled_data = [] # Reset for next batch

# Write any remaining items
if labeled_data:
    batch_num += 1
    with open(f'labeled_data_batch_{batch_num}.json', 'w') as f:
        json.dump(labeled_data, f, indent=2)