import logging
from openai import OpenAI
import json
import time
from myLlama import generate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI()

def create_file(filepath, purpose='assistants'):
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
def append_content_w_images(prompt, images):
    content = []  # Method 1 implementation
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

# Assistant Functions
# Initialize Assistant
def initialize_assistant(name, system_prompt, tools, model, files):
    logger.info('Initializing agent')
    try:
        if len(files) > 0:
            if tools is not None:
                assistant = client.beta.assistants.create(
                    name=name,
                    instructions=system_prompt,
                    tools=tools,
                    model=model,
                    tool_resources={
                        "code_interpreter": {
                            "file_ids": files
                        }
                    }
                )
            else:
                assistant = client.beta.assistants.create(
                    name=name,
                    instructions=system_prompt,
                    model=model,
                    tool_resources={
                        "code_interpreter": {
                            "file_ids": files
                        }
                    }
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
        logger.info("Assistant initialized")
        return assistant
    except Exception as e:
        logger.error(f"Failed to initialize agent: Caught {e.__class__.__name__}: {e}")

# Initialize Thread
def initialize_thread():
    try:
        logger.info('Creating thread')
        thread = client.beta.threads.create()
        logger.info('Thread created')
        return thread
    except Exception as e:
        logger.error(f"Failed to initialize thread: Caught {e.__class__.__name__}: {e}")

# run steps
def get_run_steps(run, thread_id):
    # Retrieve and process the run steps
    return client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id, order="asc")

def get_messages_from_thread(thread_id, order='asc'):
    return client.beta.threads.messages.list(
        thread_id=thread_id,
        order=order,
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

# Agent class
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
        self.assistant = initialize_assistant(name, system_prompt, tools, model, files)
        self.thread = None
        self.run = None
        self.messages = []
        self.file_comments = []

    def add_message(self, content):
        message = client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=content
        )

    # chat method
    def chat(self, msg, additional_prompt=None, images=None, files=None):
        if self.thread is None:
            self.thread = initialize_thread()

        if images is not None:
            content = append_content_w_images(msg, images)
        else:
            content = msg
        self.add_message(content)
        self.wait_on_run(self.thread.id, additional_prompt)
        if self.files is not None:
            if len(self.files) >= 1:
                self.assistant = initialize_assistant(self.name, self.system_prompt, self.tools, self.model, self.files)
        self.messages = get_messages_from_thread(self.thread.id)
        print_messages_out(self.messages)

    def go_through_tool_actions(self, tool_calls, run, thread_id):
        logger.info('Going through tool actions')
        tool_output_list = []
        for tool_call in tool_calls:
            try:
                function_name = json.loads(tool_call.json())['function']['name']
                logger.info(f'{function_name}')
                if function_name == 'delegate_instructions':
                    files = json.loads(json.loads(tool_call.json())['function']['arguments'])['files']
                    for file in files:
                        full_filename = file['file_name'] + "." + file['file_type']
                        full_path = 'sandbox/' + full_filename

                        if file['job_type'] == 'NEW':
                            full_instructions = file['instructions']
                        else:
                            with open(full_path, "r") as file_in:
                                full_instructions = "here is the current status of the file \n" + file_in.read()
                        logger.info('Generating content')
                        full_prompt = """PROMPT: You must respond in the following format:
                        {"type": type of file to use (options: python, text, html, other),
                        "content": raw content (ex: "print('hello world')"),
                        "comments": any comments to include (ex: "install pandas, etc")}""" + full_instructions
                        content = generate(full_prompt, format='json')
                        logger.info('Generating content')
                        with open(full_path, "wb") as file_out:
                            file_out.write(json.loads(content)['content'].encode())
                            self.file_comments.append(json.loads(content)['comments'])
                        logger.info('File created ' + full_path)
                        file_append = create_file(full_path)
                        self.files.append(file_append.id)
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

        while self.run.status in ["queued", "in_progress"]:
            # Retrieve updated run status
            self.run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=self.run.id)
            # Handle completed run

            # Handle run that requires action
            if self.run.status == 'requires_action':
                logger.info('Requires action')
                # Get the tool calls that require action
                tool_calls = self.run.required_action.submit_tool_outputs.tool_calls
                # Submit the collected tool outputs and return the run object
                self.go_through_tool_actions(tool_calls=tool_calls, run=self.run, thread_id=thread_id)
                self.run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=self.run.id)
            else:
                # Sleep briefly to avoid spamming the API with requests
                time.sleep(0.1)

        if self.run.status == 'completed':
            logger.info('Run complete')
            self.run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=self.run.id)
        logger.info('Finished waiting')
