import logging
from openai import OpenAI
import json
import time
from myLlama import generate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI()

def initialize_assistant(name, system_prompt, model, tools=None, files=[]):
    logger.info('Initializing agent')
    try:
        assistant_kwargs = {
            "name": name,
            "instructions": system_prompt,
            "model": model
        }

        if tools is not None:
            assistant_kwargs["tools"] = tools

        if len(files) > 0:
            assistant_kwargs["tool_resources"] = {
                "code_interpreter": {
                    "file_ids": files
                }
            }

        assistant = client.beta.assistants.create(**assistant_kwargs)
        logger.info("Assistant initialized")
        return assistant
    except Exception as e:
        logger.error(f"Failed to initialize agent: Caught {e.__class__.__name__}: {e}")

def retrieve_assistant(assistant_id):
    try:
        logger.info('retrieving assistant')
        return client.beta.assistants.retrieve(assistant_id=assistant_id)
    except Exception as e:
        logger.error(f"Failed to retrieve assistant: Caught {e.__class__.__name__}: {e}")

def retrieve_thread(thread_id):
    try:
        logger.info('retrieving thread')
        return client.beta.threads.retrieve(thread_id=thread_id)
    except Exception as e:
        logger.error(f"Failed to retrieve thread: Caught {e.__class__.__name__}: {e}")

def initialize_thread():
    try:
        logger.info('Creating thread')
        thread = client.beta.threads.create()
        return thread
    except Exception as e:
        logger.error(f"Failed to initialize thread: Caught {e.__class__.__name__}: {e}")

def create_file(filepath, purpose='assistants'):
    file = client.files.create(
        file=open(filepath, "rb"),
        purpose=purpose
    )
    return file

def encode_image_file(image_path):
    file = client.files.create(
        file=open(image_path, "rb"),
        purpose="vision"
    )
    return file

def append_content_w_images(prompt, images):
    content = []
    content.append({"type": "text", "text": prompt})
    for image in images:
        file = encode_image_file(image)
        content.append({
            "type": "image_file",
            "image_file": {
                "file_id": file.id,
            }
        })
    return content

def get_run_steps(run, thread_id):
    try:
        logger.info('getting run steps')
        return client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id, order="asc")
    except Exception as e:
        logger.error(f"Failed to get run steps: Caught {e.__class__.__name__}: {e}")

def get_messages_from_thread(thread_id, after=None, order='asc'):
    params = {
        "thread_id": thread_id,
        "order": order,
    }
    if after:
        params["after"] = after

    messages_page = client.beta.threads.messages.list(**params)
    return list(messages_page)

def print_messages(messages):
    print('=========================================')
    print("               messages ")
    print('-----------------------------------------')
    for message in messages:
        msg_value = message.content[0].text.value
        msg_role = message.role
        print(f'{msg_role}: {msg_value}')
    print('=========================================')

class Agent:
    def __init__(self, system_prompt="You are a helpful chat based assistant",
                 name='AgentGpt',
                 model='gpt-3.5-turbo-1106',
                 tools=None,
                 files=[]):
        self.system_prompt = system_prompt
        self.name = name
        self.model = model
        self.tools = tools
        self.files = files
        self.assistant = None
        self.thread = None
        self.run = None
        self.messages = []
        self.file_comments = []
        self.print_messages = []
        self.last_message_id = None  # Track the last message ID

    def add_message(self, content):
        message = client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=content
        )
        if not isinstance(self.messages, list):
            self.messages = []
        self.messages.append(message)

    def chat(self, msg, additional_prompt=None, images=None, files=None):
        if self.assistant is None:
            logger.info('no assistant found')
            self.assistant = initialize_assistant(self.name, self.system_prompt, self.model, self.tools, self.files)

        if self.thread is None:
            logger.info('no thread found')
            self.thread = initialize_thread()

        self.add_message(msg)
        self.wait_on_run(self.thread.id, additional_prompt)
        if self.files is not None:
            if len(self.files) >= 1:
                self.assistant = initialize_assistant(self.name, self.system_prompt, self.model, self.tools, self.files)
        
        # Fetch messages after the last processed message ID
        self.messages = get_messages_from_thread(self.thread.id, self.last_message_id)
        if self.messages:
            self.last_message_id = self.messages[-1].id  # Update the last message ID
        
        self.print_messages = print_messages(self.messages)
        
        # Return the messages for the response
        return [message.content[0].text.value for message in self.messages if message.role == 'assistant']

    def go_through_tool_actions(self, tool_calls, run, thread_id):
        logger.info('Going through tool actions')
        tool_output_list = []
        
        for tool_call in tool_calls:
            try:
                function_name = json.loads(tool_call.json())['function']['name']
                logger.info(function_name)

                if function_name == 'delegate_instructions':
                    files = json.loads(json.loads(tool_call.json())['function']['arguments'])['files']
                    self.process_delegate_instructions(files)
                    tool_output_list.append({"tool_call_id": tool_call.id, "output": 'file/files successfully created'})
                else:
                    tool_output_list.append({"tool_call_id": tool_call.id, "output": "something went wrong please ask the user for help"})
            
            except Exception as e:
                logger.error(f"Failed tool call {function_name}: Caught {e.__class__.__name__}: {e}")
                tool_output_list.append({"tool_call_id": tool_call.id, "output": "something went wrong please ask the user for help"})
        
        client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run.id, tool_outputs=tool_output_list)
        logger.info('Done going through tool actions')

    def wait_on_run(self, thread_id, additional_instructions=None):
        logger.info('Waiting on run')
        if additional_instructions is not None:
            self.run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant.id,
                additional_instructions=additional_instructions,
            )
        else:
            self.run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant.id,
            )
        logger.info('Requires action')
        while self.run.status in ["queued", "in_progress"]:
            # Retrieve updated run status
            self.run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=self.run.id)
            # Handle run that requires action
            if self.run.status == 'requires_action':
                
                # Get the tool calls that require action
                tool_calls = self.run.required_action.submit_tool_outputs.tool_calls
                # Submit the collected tool outputs and return the run object
                self.go_through_tool_actions(tool_calls=tool_calls, run=self.run, thread_id=thread_id)
                self.run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=self.run.id)
            else:
                self.run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=self.run.id)
                # Sleep briefly to avoid spamming the API with requests
                time.sleep(0.1)

        if self.run.status == 'completed':
            logger.info('Run complete')
            self.run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=self.run.id)
        logger.info('Finished waiting')

    def process_delegate_instructions(self, files):
        for file in files:
            full_filename = f"{file['file_name']}{file['file_type']}"
            full_path = f'sandbox/{full_filename}'

            if file['job_type'] == 'NEW':
                full_instructions = file['instructions']
            else:
                with open(full_path, "r") as file_in:
                    full_instructions = f"here is the current status of the file \n{file_in.read()}"
            
            logger.info('Generating content')
            full_prompt = (
                "PROMPT: You must respond in the following format:\n"
                '{"type": type of file to use (options: .py,.txt,ect),\n'
                '"content": raw content (ex: "print(\'hello world\')"),\n'
                '"comments": any comments to include (ex: "install pandas, etc")}\n' 
                + full_instructions
            )
            content = generate(full_prompt, format='json')
            logger.info('Content generated')
            
            with open(full_path, "wb") as file_out:
                file_out.write(json.loads(content)['content'].encode())
                self.file_comments.append(json.loads(content)['comments'])
            
            logger.info(f'File created {full_path}')
            file_append = create_file(full_path)
            self.files.append(file_append.id)