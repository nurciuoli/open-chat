import requests
import os
from dotenv import load_dotenv
import logging
import time
from openai import OpenAI

# Load environment variables and configure logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

logging.info("Perplexity configuration initialized.")

client = OpenAI(
    api_key=PERPLEXITY_API_KEY,
    base_url="https://api.perplexity.ai",
)
logging.info("OpenAI client initialized.")


# Agent class definition
class Agent:
    """Agent class for interacting with OpenAI's API."""
    def __init__(self, system_prompt='You are a helpful assistant', model="llama-3.1-sonar-large-128k-chat",messages=[], max_tokens=4096, temperature=0.5,**kwargs):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.history = messages
        self.model = model
        self.response = None
        logging.info(f"Perplexity agent created with model {model}.")

        if messages==[]:
            messages.append({'role':'system','content':system_prompt})
            self.messages=messages
        else:
            self.messages=messages
        

    def chat(self, prompt):
        """Initiate chat with the assistant"""
        self.messages.append({'role':'user','content':prompt})
        

        self.response = client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
        self.messages.append({'role':'assistant','content':self.response.choices[0].message.content})

        #print(self.response.choices[0].message.content)
        
        logging.info("Chat completed.")

