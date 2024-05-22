from openai import OpenAI
client = OpenAI()
import json

# Function to encode the image into OA file format
def encode_image_file(image_path):
    file = client.files.create(
    file=open(image_path, "rb"),
    purpose="vision"
    )
    return file

# Append image files to content list
def append_content_w_images(prompt,images):
    content=[] # Method 1 implementation
    content.append(
    {"type": "text", "text": prompt})
    for image in images:
        file = encode_image_file(image)
        content.append({
        "type": "image_file",
        "image_file": {
            "file_id": file.id,
        }})
    return content
 
# Assistant Functions
# Initialize Assistant
def initialize_assistant(agent):
    try:
        if agent.tools is not None:
            agent.assistant = client.beta.assistants.create(
                name=agent.name,
                instructions=agent.system_prompt,
                tools=agent.tools,
                model=agent.model,
                )
        else:
            agent.assistant = client.beta.assistants.create(
                name=agent.name,
                instructions=agent.system_prompt,
                model=agent.model,
            )
        print("checkpoint: assistant initialized")
    except Exception as e:
        # handle the exception
        print(f"Failed to initailize agent: Caught {e.__class__.__name__}: {e}")

# Initialize Thread
def initialize_thread(agent):
    try:
        agent.thread = client.beta.threads.create()
        print('checkpoint: thread created')
    except Exception as e:
        # handle the exception
        print(f"Failed to initailize thread: Caught {e.__class__.__name__}: {e}")

# Go through messages and print content
def add_msg_content_to_list(messages):
    out_msgs = []
    for full_msg in json.loads(messages.json())['data']:
        role = full_msg['role']
        for message in full_msg['content']:
            if message['type']=='text':
                print(role+': '+message['text']['value'])
                out_msgs.append(message['text']['value'])
    
    return out_msgs

# Agent class
class Agent:
    def __init__(self,system_prompt="You are a helpful chat based assistant",
                 name = 'AgentGpt',
                 model = 'gpt-3.5-turbo-1106',
                 tools = None):
        self.system_prompt = system_prompt
        self.name = name
        self.model = model
        self.tools = tools
        initialize_assistant(self)
        self.thread = None
        self.messages=[]
    # chat method
    def chat(self,msg,additional_prompt = "remember to double check your work",images=None,files=None):
        if self.thread is None:
            initialize_thread(self)

        if images is not None:
           content =append_content_w_images(msg,images)
        else:
           content = msg
        
        message = client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=content
            )
        print('checkpoint: msg created')
        self.messages.append(message)
        count_msg = len(self.messages)

        self.run = client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions=additional_prompt)
        print('checkpoint: run started')
        if self.run.status == 'completed': 
            self.messages = client.beta.threads.messages.list(
                thread_id=self.thread.id,
                order = 'asc',
            )
            print('checkpoint: run complete')
            out_messages = add_msg_content_to_list(self.messages)
            return out_messages[count_msg:]
        else:
            print(self.run.status)





