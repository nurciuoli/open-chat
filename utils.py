import os
import json

def load_agent_state(agent_data):
    """
    Loads the state of the agent based on the provided agent data.
    This example assumes that the agent's state is stored in a JSON file named after the agent's name.
    """
    file_path = os.path.join('data', f"{agent_data['name']}.json")
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            state = json.load(file)
        return state
    else:
        return None

def get_file_content(filename: str) -> str:
    filepath = os.path.join('sandbox', filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as file:
        content = file.read()
    return content
