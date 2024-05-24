from openai import OpenAI
client = OpenAI()
import json
import time
from myLlama import generate

def create_file(filepath,purpose='assistants'):
    file = client.files.create(
    file=open(filepath, "rb"),
    purpose=purpose
    )
    return file


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
def initialize_assistant(name,system_prompt,tools,model,files):
    print('cp: initializing agent')
    try:
        if len(files)>0:
            if tools is not None:
                assistant = client.beta.assistants.create(
                    name=name,
                    instructions=system_prompt,
                    tools=tools,
                    model=model,
                    tool_resources={
                        "code_interpreter": {
                        "file_ids": files
                        }}
                )

            else:
                assistant = client.beta.assistants.create(
                    name=name,
                    instructions=system_prompt,
                    model=model,
                    tool_resources={
                        "code_interpreter": {
                        "file_ids": files
                        }}
                )
        else:
            if tools is not None:
                assistant = client.beta.assistants.create(
                    name=name,
                    instructions=system_prompt,
                    tools=tools,
                    model=model,
                    )
            else:
                assistant = client.beta.assistants.create(
                    name=name,
                    instructions=system_prompt,
                    model=model,
                )
        print("cp: assistant initialized")
        return assistant
    except Exception as e:
        # handle the exception
        print(f"Failed to initailize agent: Caught {e.__class__.__name__}: {e}")

# Initialize Thread
def initialize_thread():
    try:
        print('cp: creating thread')
        thread = client.beta.threads.create()
        print('cp: thread created')
        return thread
    except Exception as e:
        # handle the exception
        print(f"Failed to initailize thread: Caught {e.__class__.__name__}: {e}")

# run steps
def get_run_steps(run,thread_id):
    # Retrieve and process the run steps
    return client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id, order="asc")

def go_through_tool_actions(tool_calls,run,thread_id):
    print('cp: going through tool actions')
    tool_output_list = []
    agent_files=[]
    for tool_call in tool_calls:
        try:
            function_name = json.loads(tool_call.json())['function']['name']
            print(f'cp: {function_name}')
            if function_name=='delegate_instructions':
                files = json.loads(json.loads(tool_call.json())['function']['arguments'])['files']
                for file in files:
                    full_filename = file['file_name']+"."+file['file_type']
                    full_path = 'sandbox/'+full_filename
                    with open(full_path, "w") as file_out:
                        content = generate(file['instructions'])
                        print('cp: generating content')
                        file_out.write(content)
                    file_out = create_file(full_path)
                    agent_files.append(file_out.id)
                tool_output_list.append({"tool_call_id": tool_call.id,"output": f'file/files successfully created'})
            else:
                tool_output_list.append({"tool_call_id": tool_call.id,"output": "something went wrong"})

        except Exception as e:
            # handle the exception
            print(f"Failed tool call {function_name}: Caught {e.__class__.__name__}: {e}")
        
    client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run.id, tool_outputs=tool_output_list)
    print('cp: done going through tool actions')
    return agent_files

def get_messages_from_thread(thread_id,order = 'asc'):
    return client.beta.threads.messages.list(
                thread_id=thread_id,
                order = order,
            )


def print_messages_out(messages):
    print('=========================================')    
    print("               messages ")
    print('-----------------------------------------')
    for message in messages:
        assert message.content[0].type == "text"
        msg_value = message.content[0].text.value
        msg_role = message.role
        print(f'{msg_role}: {msg_value}')
    print('=========================================')
        

def wait_on_run(assistant_id,thread_id,additional_instructions=None):
        agent_files = None
        print(f'cp: waiting on run')
        if additional_instructions is not None:
            run=client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=assistant_id,
                    additional_instructions=additional_instructions,
                )
        else:
            run=client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=assistant_id,
                )
        while run.status in ["queued", "in_progress"]:
            # Retrieve updated run status
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            # Handle completed run
            if run.status == 'completed':
                print('cp: run complete')
                run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)


            # Handle run that requires action
            elif run.status == 'requires_action':
                print('cp: requires action')
                # Get the tool calls that require action
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                # Submit the collected tool outputs and return the run object
                agent_files = go_through_tool_actions(tool_calls=tool_calls,run=run,thread_id = thread_id)
                run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

                

            else:
                # Sleep briefly to avoid spamming the API with requests
                time.sleep(0.1)
                run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            

        print('cp: finished waiting')
        return (run,agent_files)

# Agent class
class Agent:
    def __init__(self,system_prompt="You are a helpful chat based assistant",
                 name = 'AgentGpt',
                 model = 'gpt-3.5-turbo-1106',
                 tools = None,
                 files=[]):
        self.system_prompt = system_prompt
        self.name = name
        self.model = model
        self.tools = tools
        self.files=files
        self.assistant = initialize_assistant(name,system_prompt,tools,model,files)
        self.thread = None
        self.run=None
        self.messages=[]
        
    
    def add_message(self,content):
        message = client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=content
            )
        self.messages.append(message)

    # chat method
    def chat(self,msg,additional_prompt = None,images=None,files=None):
        if self.thread is None:
            self.thread=initialize_thread()

        if images is not None:
           content =append_content_w_images(msg,images)
        else:
           content = msg
        self.add_message(content)
        self.run,self.files =wait_on_run(self.assistant.id,self.thread.id,additional_prompt)
        self.messages = get_messages_from_thread(self.thread.id)
        print_messages_out(self.messages)
