from openai import OpenAI
import base64
import json
import os
from dotenv import load_dotenv
import logging

# Load environment variables and configure logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logging.info("OpenAI client initialized.")

# Function to encode the image to base64
def encode_image(image_path):
    """Encode image file to base64 string."""
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    logging.info(f"Image {image_path} encoded to base64.")
    return encoded_image

# Function to submit a message to a thread
def submit_message(assistant_id, thread, user_message, response_format=None):
    """Submit a message to a thread and create a run with optional response format."""
    if response_format:
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_message)
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id, response_format=response_format)
    else:
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_message)
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)
    logging.info(f"Message submitted to thread {thread.id} with run {run.id}.")
    return run

# Function to get responses from a thread
def get_response(thread):
    """Retrieve list of messages from a thread in ascending order."""
    responses = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    logging.info(f"Responses retrieved for thread {thread.id}.")
    return responses

# Function to create a thread and submit a run
def create_thread_and_run(user_input, assistant_id):
    """Create a new thread and submit a user message as a run."""
    thread = client.beta.threads.create()
    run = submit_message(assistant_id, thread, user_input)
    logging.info(f"Thread {thread.id} created and run submitted.")
    return thread, run

import time

# Pretty printing helper function
def pretty_print(messages):
    """Pretty print messages and return a list of message dictionaries."""
    out_txt = []
    logging.info("# Messages")
    for m in messages:
        logging.info(f"{m.role}: {m.content[0].text.value}")
        out_txt.append({"role": f"{m.role}", "content": f"{m.content[0].text.value}"})
    return out_txt

# Function to wait on a run to complete
def wait_on_run(run, thread):
    """Wait for a run to complete and return the final run status."""
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(0.5)
    logging.info(f"Run {run.id} completed with status {run.status}.")
    return run

# Agent class definition
class Agent:
    """Agent class for interacting with OpenAI's API."""
    def __init__(self, system_prompt='You are a helpful assistant', model='gpt-3.5-turbo',messages=[], max_tokens=4096, temperature=0.5, name='Chatbot GPT', tools=None):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.history = messages
        self.model = model
        self.response = None
        self.assistant = client.beta.assistants.create(name=name, instructions=system_prompt, model=model)
        logging.info(f"Assistant {name} created with model {model}.")
        
        if tools:
            self.assistant = client.beta.assistants.update(self.assistant.id, tools=tools)
            logging.info(f"Assistant {name} updated with tools.")

        self.run = None
        self.thread = None
        self.response = None
        self.messages = None

    def chat(self, prompt, images=None, json_mode=False):
        """Initiate chat with the assistant, handling text and optional images."""
        logging.info('GPT chat initiated.')
        if not self.thread:
            if len(self.history)>0:
                self.thread = client.beta.threads.create(messages=self.history)
            else:
                self.thread = client.beta.threads.create()
            logging.info(f"New thread {self.thread.id} created.")

        content = [{"type": "text", "text": prompt}]
        if images:
            for image in images:
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}})
                logging.info("Image added to chat content.")

        response_format = {"type": "json_object"} if json_mode else None

        self.run = submit_message(self.assistant.id, self.thread, content, response_format)
        self.run = wait_on_run(self.run, self.thread)
        self.response = get_response(self.thread)
        self.messages = pretty_print(self.response)
        self.history = self.response.to_dict()['data']
        logging.info("Chat completed.")
