import os
import json



def load_json(path):
    with open(path, 'r') as file:
        data = json.load(file)

    return data



def save_json(json_data, path):
    with open(path, 'w') as file:
        json.dump(json_data, file, indent=2)   
