import logging
import json
import time
from agents.oa.api import initialize_thread, get_messages_from_thread,initialize_assistant, list_threads, get_run_steps,retrieve_assistant,retrieve_thread
from agents.oa.utils import create_file, encode_image_file, append_content_w_images
from agents.myLlama import generate
import logging
from openai import OpenAI

client = OpenAI()

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, system_prompt, name, model):
        self.system_prompt = system_prompt
        self.name = name
        self.model = model
        self.assistant = None
        self.thread = None
        self.messages = []
        self.files = []
        self.print_count = 0
        self.tools = None

    def to_dict(self):
        # Implement serialization logic
        return {
            "assistant_id": self.assistant.id,
            "thread_id": self.thread.id,
        }
    
    def from_dict(self,agentdata):
        self.assistant = retrieve_assistant(agentdata['assistant_id'])
        self.thread = retrieve_thread(agentdata['thread_id'])
        self.messages = get_messages_from_thread(self.thread.id)


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
        self.messages = get_messages_from_thread(self.thread.id)

        out_messages = [message.content[0].text.value for message in self.messages if message.role == 'assistant'][self.print_count:]
        self.print_count += 1
        # Return the messages for the response
        return out_messages

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