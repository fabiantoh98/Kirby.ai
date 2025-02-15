import json
import random

def sample_json_data(input_file, output_file, sample_size):
    """
    Sample a specified number of items from a JSON list and write to output file.
    
    Args:
        input_file (str): Path to input JSON file
        output_file (str): Path to output JSON file 
        sample_size (int): Number of items to sample
    """
    # Read input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Sample random items
    if len(data) > sample_size:
        sampled_data = random.sample(data, sample_size)
    else:
        sampled_data = data
        
    # Write sampled data to output file
    with open(output_file, 'w') as f:
        json.dump(sampled_data, f, indent=4)

if __name__ == "__main__":
    # Example usage
    sample_json_data("big_data.json", 
                     "sampled_data.json",
                     sample_size=250)
