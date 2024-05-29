import json
import os
from typing import Optional
from myLlama import generate
from myGpt import Agent  # Make sure to import the Agent class properly
from myGpt import Agent
from utils import load_agent_state

import logging
DATA_DIR = 'data'

agent = None

import os
import json

DATA_DIR = 'data'

import os
import json
from typing import List

logger = logging.getLogger(__name__)


def initialize_agent(agent_data: dict) -> Optional[Agent]:
    try:
        agent = Agent(
            system_prompt=agent_data.get("system_prompt", "You are a helpful chat based assistant"),
            name=agent_data.get("name", "AgentGpt"),
            model=agent_data.get("model", "gpt-3.5-turbo-1106"),
            tools=agent_data.get("tools", []),
            files=agent_data.get("files", [])
        )
        return agent
    except Exception as e:
        print(f"Error initializing agent: {e}")
        return None



def handle_chat(agent_data, msg):
    try:
        # Load or initialize the agent based on the provided agent data
        agent_state = load_agent_state(agent_data)
        
        if agent_state:
            logger.info("Loaded existing agent state.")
            agent = Agent(**agent_state)
        else:
            logger.info("Initializing new agent.")
            agent = Agent(
                system_prompt=agent_data['system_prompt'],
                name=agent_data['name'],
                model=agent_data['model']
            )
        
        if not agent:
            logger.error("Failed to initialize agent.")
            return None, "Failed to initialize agent"

        # Process the chat message
        logger.info("Processing chat message.")
        agent.chat(msg)
        logger.info("Processing chat message.")
        
        
        return agent

    except Exception as e:
        logger.error(f"Exception during chat handling: {e}")
        return None, str(e)


def save_chat_session(thread_id: str):
    filepath = os.path.join(DATA_DIR, 'chat_sessions.json')

    # Load existing sessions or initialize an empty list
    if not os.path.exists(filepath):
        sessions = []
    else:
        with open(filepath, 'r') as file:
            sessions = json.load(file)

    # Append the new thread ID to the list if it doesn't already exist
    if thread_id not in sessions:
        sessions.append(thread_id)

    # Save the updated list of sessions back to the file
    with open(filepath, 'w') as file:
        json.dump(sessions, file, indent=4)

def load_message_history(thread_id: str) -> Optional[list]:
    filepath = os.path.join(DATA_DIR, 'message_history.json')
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as file:
        history = json.load(file)
    return history.get(thread_id, None)

def save_agent_template(template_data: dict):
    filepath = os.path.join(DATA_DIR, 'agent_templates.json')
    if not os.path.exists(filepath):
        templates = []
    else:
        with open(filepath, 'r') as file:
            templates = json.load(file)
    templates.append(template_data)
    with open(filepath, 'w') as file:
        json.dump(templates, file)

def load_agent_templates() -> list:
    filepath = os.path.join(DATA_DIR, 'agent_templates.json')
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as file:
        templates = json.load(file)
    return templates
