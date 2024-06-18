import anthropic
import json
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the Anthropic client
client = anthropic.Anthropic()
logging.info("Anthropic client initialized.")

# Function to send messages to the Anthropic API
def send_message(messages, system_prompt, model, max_tokens, temperature):
    """
    Sends a message to the Anthropic API and returns the response content.

    Parameters:
    - messages: A list of message dictionaries.
    - system_prompt: The system prompt string.
    - model: The model identifier string.
    - max_tokens: The maximum number of tokens to generate.
    - temperature: The temperature for the generation.

    Returns:
    - The content of the response from the API.
    """
    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=messages
        )
        return message.content
    except Exception as e:
        logging.error(f"Error sending message to Anthropic API: {e}")
        return None

# Agent class for managing interactions
class Agent:
    def __init__(self, system_prompt='You are a helpful assistant',
                 name='assistant',
                 model="claude-3-sonnet-20240229",
                 messages=[],
                 max_tokens=1000,
                 temperature=0.5,
                 tools=None):
        """
        Initializes the Agent with default values or provided arguments.

        Parameters:
        - system_prompt: The default system prompt for the agent.
        - name: The name of the agent.
        - model: The model identifier for the agent.
        - max_tokens: The maximum number of tokens for the agent's responses.
        - temperature: The temperature for the agent's responses.
        """
        self.system_prompt = system_prompt
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.name = name
        self.response = None
        self.messages = messages

    def __str__(self):
        # String representation of the Agent
        return f"Agent(Name: {self.name}, Model: {self.model})"

    def chat(self, user_prompt, attachments=None, json_mode=False):
        """
        Handles chatting with the user, processing attachments, and managing response modes.

        Parameters:
        - user_prompt: The user's input prompt.
        - attachments: Optional attachments to include in the prompt.
        - json_mode: Flag to determine if the response should be in JSON format.

        Returns:
        - The response from the agent.
        """
        logging.info(f"Chat initiated with prompt: {user_prompt}")
        full_prompt = ''
        if attachments is not None:
            for attachment in attachments:
                tag_label = attachment['name']
                full_prompt += f"<{tag_label}> {attachment['content']} </{tag_label}>"
        else:
            full_prompt = user_prompt

        self.messages.append({"role": "user", "content": full_prompt})

        if json_mode==True:
            self.messages.append({"role": "assistant", "content": "{"})

        response = send_message(self.messages, self.system_prompt, self.model, self.max_tokens, self.temperature)

        self.response = response
        self.print_response_and_append_messages(response, json_mode)
        return response

    def print_response_and_append_messages(self, response, json_mode):
        """
        Processes and prints the response messages, appending them to the messages list.

        Parameters:
        - response: The response to process.
        - json_mode: Flag to determine if the response should be processed as JSON.
        """
        try:
            for message in response:
                message_json = json.loads(message.json())
                if json_mode:
                    temp_response = "{" + json.loads(self.response[0].json())['text']
                    self.messages[-1] = {'role': self.name, 'content': temp_response}
                elif 'text' in message_json:
                    print(message_json['text'])
                    self.messages.append({'role': self.name, 'content': message_json['text']})
        except Exception as e:
            logging.error(f"Error processing response messages: {e}")
