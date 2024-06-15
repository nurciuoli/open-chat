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


# Agent class framework for interacting with Google's generative AI models
class Agent:
    def __init__(self, model='gemini-1.5-pro-latest', system_prompt='You are a helpful assistant', messages=[],tools=None, max_tokens=8000, temperature=0.5):
        """Initialize the agent with model details and configuration."""
        self.response = None
        self.messages = messages
        self.thread = None
        self.model_id = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.tools = tools
        self.system_prompt = system_prompt
        self.model = None
        logging.info(f"Agent initialized with model {model}")

    def generate(self, user_msg, json_mode=False):
        """Generate a response from the model based on the user message."""
        response_type = {"response_mime_type": "application/json"} if json_mode else None
        try:
            if response_type:
                self.response = self.model.generate_content(user_msg)
            else:
                self.response = self.model.generate_content(user_msg, generation_config=response_type)
            logging.info("Gemini Response generated successfully.")
        except Exception as e:
            logging.error(f"Error generating Gemini response: {e}")
        print(self.response.text)
        return self.response.text

    def review_content(self, content, json_mode=False):
        """Review content using the model."""
        try:
            self.response = self.model.generate_content(content)
            logging.info("Content reviewed successfully.")
        except Exception as e:
            logging.error(f"Error reviewing content: {e}")
        return self.response.text

    def chat(self, user_msg, json_mode=False, auto_funct_call=False):
        """Initiate a chat session with the model."""
        response_type = "application/json" if json_mode else "text/plain"
        try:
            if self.tools is not None:
                self.model = genai.GenerativeModel(self.model_id, tools=self.tools, system_instruction=self.system_prompt, generation_config=genai.GenerationConfig(max_output_tokens=self.max_tokens, temperature=self.temperature, response_mime_type=response_type))
            else:
                self.model = genai.GenerativeModel(self.model_id, system_instruction=self.system_prompt, generation_config=genai.GenerationConfig(max_output_tokens=self.max_tokens, temperature=self.temperature, response_mime_type=response_type))
            logging.info("Gemini Model loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load Gemini model: {e}")

        self.thread = self.model.start_chat(history=self.messages, enable_automatic_function_calling=auto_funct_call)
        logging.info("Gemini Chat session started.")

        try:
            if response_type:
                self.response = self.thread.send_message(content=[user_msg])
            else:
                self.response = self.thread.send_message(content=[user_msg], generation_config=response_type)
            self.messages.append({'role': 'user', 'content': user_msg})
            self.messages.append({'role': 'assistant', 'content': self.response.text})
            logging.info("Gemini Message sent and response received.")
        except Exception as e:
            logging.error(f"Failed to send message or receive response from Gemini: {e}")
        print(self.response.text)
        return self.response.text
