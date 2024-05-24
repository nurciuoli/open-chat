from openai import OpenAI
client = OpenAI()
import json
import time

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
    print('cp: initializing agent')
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
        print("cp: assistant initialized")
    except Exception as e:
        # handle the exception
        print(f"Failed to initailize agent: Caught {e.__class__.__name__}: {e}")

# Initialize Thread
def initialize_thread(agent):
    try:
        print('cp: creating thread')
        agent.thread = client.beta.threads.create()
        print('cp: thread created')
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

def get_run_steps(run,thread_id):
    # Retrieve and process the run steps
    return client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id, order="asc")

def go_through_tool_actions(tool_calls,run,thread_id):
    print('cp: going through tool actions')
    tool_output_list = []
    for tool_call in tool_calls:
        function_name = json.loads(tool_call.json())['function']['name']
        print(f'cp: {function_name}')
        tool_output_list.append({"tool_call_id": tool_call.id,"output": "the work is done and in the project folder"})


    # Submit the collected tool outputs and return the run object
    run = client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run.id, tool_outputs=tool_output_list)

    print('cp: done going through tool actions')

    return run
            
def print_messages_out(messages):
    print("               messages ")
    print('-----------------------------------------')
    for message in messages:
        assert message.content[0].type == "text"
        msg_value = message.content[0].text.value
        msg_role = message.role
        print(f'{msg_role}: {msg_value}')

# Agent class
class Agent:
    def __init__(self,system_prompt="You are a helpful chat based assistant",
                 name = 'AgentGptnewnew',
                 model = 'gpt-3.5-turbo-1106',
                 tools = None):
        self.system_prompt = system_prompt
        self.name = name
        self.model = model
        self.tools = tools
        initialize_assistant(self)
        self.thread = None
        self.run=None
        self.messages=[]
    # chat method

    def wait_on_run(self,thread_id,additional_instructions=None):
        print(f'cp: waiting on run')
        if additional_instructions is not None:
            run=client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=self.assistant.id,
                    additional_instructions=additional_instructions,
                )
        else:
            run=client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=self.assistant.id,
                )
        while run.status in ["queued", "in_progress"]:
            # Retrieve updated run status
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            # Handle completed run
            if run.status == 'completed':
                print('cp: run complete')
                run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
                return run

            # Handle run that requires action
            elif run.status == 'requires_action':
                print('cp: requires action')
                # Get the tool calls that require action
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                # Submit the collected tool outputs and return the run object
                run = go_through_tool_actions(tool_calls=tool_calls,run=run,thread_id = thread_id)

            else:
                # Sleep briefly to avoid spamming the API with requests
                time.sleep(0.1)
            

        print('cp: finished waiting')
        return run
    
    def add_message(self,content):
        message = client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=content
            )
        print('cp: msg created')
        self.messages.append(message)

    # chat method
    def chat(self,msg,additional_prompt = None,images=None,files=None):
        print(f'cp: starting chat')
        if self.thread is None:
            initialize_thread(self)

        if images is not None:
           content =append_content_w_images(msg,images)
        else:
           content = msg
        
        self.add_message(content)

        self.run = self.wait_on_run(self.thread.id,additional_prompt)

        self.messages = client.beta.threads.messages.list(
                thread_id=self.thread.id,
                order = 'asc',
            )
        
        print('=========================================')
        
        print_messages_out(self.messages)

        print('=========================================')

