from openai import OpenAI
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  

def submit_message(assistant_id, thread, user_message,response_format = None):
    if response_format:
        client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=user_message,
        )
        return client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,response_format=response_format,
        )
    else:
        client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=user_message
        )
        return client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def create_thread_and_run(user_input,assistant_id):
    thread = client.beta.threads.create()
    run = submit_message(assistant_id, thread, user_input)
    return thread, run

import time
import json
# Pretty printing helper
def pretty_print(messages):
    out_txt=[]
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
        out_txt.append({"role":f"{m.role}","content":f"{m.content[0].text.value}"})
    return out_txt


# Waiting in a loop
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


class Agent:
    def __init__(self,system_prompt='You are a helpful assistant',model='gpt-3.5-turbo',
                 max_tokens = 4096, temperature = 0.5,name = 'Chatbot GPT',tools=None):
        
        self.max_tokens = max_tokens
        self.temperature = temperature
        """Initializes the object"""
        # Initialize instance variables here
        self.history=[]
        self.model=model
        self.response=None
        self.assistant = client.beta.assistants.create(
                name=name,
                instructions=system_prompt,
                model=model,
            )
        
        if tools:
            self.assistant = client.beta.assistants.update(
                self.assistant.id,
                tools=tools,
            )

        self.run=None
        self.thread=None
        self.response=None
        self.messages=None


    def chat(self,prompt,images=None,json_mode=False):
        print('gpt chat')

        if not self.thread:
            self.thread= client.beta.threads.create()

        content=[] # Method 1 implementation
        content.append(
        {"type": "text", "text": prompt})
        if images:
            for image in images:
                content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image}",
                }})

        if json_mode==True:
            response_format = { "type": "json_object" }
        else:
            response_format=None

        self.run = submit_message(self.assistant.id, self.thread, content,response_format)

        self.run=wait_on_run(self.run,self.thread)
        self.response=get_response(self.thread)
        self.messages=pretty_print(self.response)
        self.history=self.response.to_dict()['data']
                