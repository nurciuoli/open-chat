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

def get_file(file_path):
    return client.files.retrieve(file_path)

# Quick helper function to convert our output file to a png
def convert_file_to_png(file_id, write_path):
    data = client.files.content(file_id)
    data_bytes = data.read()
    with open(write_path, "wb") as file:
        file.write(data_bytes)

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

import json

def create_file(filepath):
    return client.files.create(file=open(filepath, "rb"), purpose="assistants")

# Pretty printing helper function
def pretty_print(messages):
    """Pretty print messages and return a list of message dictionaries."""
    out_txt = []
    logging.info("# Messages")
    for m in json.loads(messages.json())['data']:
        for content_out in m['content']:
            key = list(content_out.keys())[0]
            logging.info(f"{m['role']}: {key}")
            if key=='text':
                out_txt.append({"role": f"{m['role']}", "content": f"{content_out[key]['value']}"})
    return out_txt

# Function to wait on a run to complete
def wait_on_run(run, thread):
    """Wait for a run to complete and return the final run status."""
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(0.5)
    logging.info(f"Run {run.id} completed with status {run.status}.")
    return run

import json

def show_json(obj):
    print(json.loads(obj.model_dump_json()))

def get_run_steps(thread,run):
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=thread.id, run_id=run.id, order="asc"
    )

    return run_steps

def pretty_print_run_steps(run_steps):
    input_l=[]
    output_l=[]
    for step in json.loads(run_steps.json())['data']:
        run_key = list(step['step_details'].keys())[0]
        #print(run_key)
        if run_key=='tool_calls':
            for tool_call in step['step_details']['tool_calls']:
                if list(tool_call.keys())[0]=='id':
                    tool_key = tool_call['function']['name']
                    input_l.append({tool_key:tool_call['function']['arguments']})
                else:
                    print(tool_call['code_interpreter']['input'])
                    input_l.append({'code_interpreter':tool_call['code_interpreter']['input']})
                    print(str(tool_call['code_interpreter']['outputs']))
                    output_l.append({'code_interpreter':tool_call['code_interpreter']['outputs']})
                
    return input_l,output_l

    

# Agent class definition
class Agent:
    """Agent class for interacting with OpenAI's API."""
    def __init__(self, system_prompt='You are a helpful assistant', model='gpt-3.5-turbo',messages=[], max_tokens=4096, temperature=0.5, name='Chatbot GPT', tools=None,files=[]):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.history = messages
        self.model = model
        self.response = None
        self.tools=tools
        self.assistant = client.beta.assistants.create(name=name, instructions=system_prompt, model=model)
        logging.info(f"Assistant {name} created with model {model}.")
        
        if tools:
            self.assistant = client.beta.assistants.update(self.assistant.id, tools=tools)
            logging.info(f"Assistant {name} updated with tools.")

        if files:
            uploaded_files=[]
            for file in files:
                temp_file = create_file(file)
                uploaded_files.append(temp_file.id)
            if tools:
                self.assistant = client.beta.assistants.update(self.assistant.id, tool_resources={self.tools[0]['type']:{"file_ids":uploaded_files}})
            else:
                self.assistant = client.beta.assistants.update(self.assistant.id, tool_resources={'file_search':{"file_ids":uploaded_files}})
            self.files=uploaded_files
        else:
            self.files=None

        self.run = None
        self.thread = None
        self.response = None
        self.messages = None
        
        self.tool_input=None
        self.tool_output=None

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
        if self.tools:
            self.run_steps=get_run_steps(self.thread,self.run)
            self.tool_input,self.tool_output=pretty_print_run_steps(self.run_steps)
        self.response = get_response(self.thread)
        self.history = self.response.to_dict()['data']
        self.messages = pretty_print(self.response)
        
        logging.info("Chat completed.")
