from openai import OpenAI
import base64
import json
import os
from dotenv import load_dotenv
import logging
import time

# Load environment variables and configure logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Initialize OpenAI client with API key from environment variable
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")


client = OpenAI(
    api_key=OPENAI_API_KEY,
)
logging.info("OpenAI client initialized.")


# Agent class definition
class Agent:
    """Agent class for interacting with OpenAI's API."""
    def __init__(self, system_prompt='You are a helpful assistant', model='grok-beta',messages=[], max_tokens=4096,**kwargs):
        self.max_tokens = max_tokens
        self.history = messages
        self.model = model
        self.response = None
        logging.info(f"o1 agent created with model {model}.")

        if messages==[]:
            messages.append({'role':'user','content':system_prompt})
            self.messages=messages
        else:
            self.messages=messages
        

    def chat(self, prompt):
        """Initiate chat with the assistant"""
        self.messages.append({'role':'user','content':prompt})
        

        self.response = client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    max_completion_tokens=self.max_tokens
                )
        self.messages.append({'role':'assistant','content':self.response.choices[0].message.content})

        #print(self.response.choices[0].message.content)
        
        logging.info("Chat completed.")
