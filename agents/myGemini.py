import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()



# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure the Google Generative AI with API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
logging.info("Gemini client initialized.")


class Agent:
    def __init__(self, model='gemini-1.5-pro-latest', system_prompt='You are a helpful assistant', messages=[], tools=None, max_tokens=8000, temperature=0.5,files=None):
        """Initialize the agent with model details and configuration."""
        self.response = None
        self.thread = None
        self.model_id = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.tools = tools
        self.system_prompt = system_prompt
        self.model = None
        self.messages=messages
        self.history=None
        logging.info(f"Agent initialized with model {model}")

         # Convert input messages to the required format for the history
        for message in messages:
            self.history.append({
                'role': message['role'] if message['role'] == 'user' else 'model',
                'parts': [{'text': message['content']}]
            })

    def chat(self, user_msg, json_mode=False, auto_funct_call=False):
        """Initiate a chat session with the model."""
        response_type = "application/json" if json_mode else "text/plain"
        try:
            if self.model is None:
                if self.tools is not None:
                    self.model = genai.GenerativeModel(self.model_id, tools=self.tools, system_instruction=self.system_prompt, generation_config=genai.GenerationConfig(max_output_tokens=self.max_tokens, temperature=self.temperature, response_mime_type=response_type))
                else:
                    self.model = genai.GenerativeModel(self.model_id, system_instruction=self.system_prompt, generation_config=genai.GenerationConfig(max_output_tokens=self.max_tokens, temperature=self.temperature, response_mime_type=response_type))

            if self.thread is None:
                # Start the chat session with the formatted history
                if self.history:
                    self.thread = self.model.start_chat(history=self.history, enable_automatic_function_calling=auto_funct_call)
                else:
                    self.thread = self.model.start_chat(enable_automatic_function_calling=auto_funct_call)
                
                logging.info("Gemini Chat session started.")

            # Construct the message in the expected format for the history
            formatted_user_msg = {
                'role': 'user',
                'parts': [{'text': user_msg}]
            }

            # Send the formatted message
            self.response = self.thread.send_message(formatted_user_msg)
            if self.response is not None:
                # Append the user message to the original messages list
                self.messages.append({'role': 'user', 'content': user_msg})
                # Append the user message to the history in the required format
                self.history.append(formatted_user_msg)
                # Append the model's response to the history
                formatted_model_response = {
                    'role': 'model',
                    'parts': [{'text': self.response.text}]
                }
                self.history.append(formatted_model_response)
                # Also append the model's response to the original messages list
                self.messages.append({'role': 'assistant', 'content': self.response.text})
                logging.info("Gemini Message sent and response received.")
                return self.response.text
            else:
                logging.error("Received no response from Gemini model.")
                return "No response received from model."
        except Exception as e:
            logging.error(f"Failed to send message or receive response from Gemini: {e}")
            return f"Error: {e}"