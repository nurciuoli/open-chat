import google.generativeai as genai

import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# agent class framework
class Agent:
    def __init__(self,model='gemini-1.0-pro-latest',system_prompt = 'You are a helpful assistant',tools=None,max_tokens = 8000,temperature = 0.5):
        self.response=None
        self.messages=None
        self.thread=None
        self.tools=tools
        self.system_prompt = system_prompt
        try:
            if self.tools is not None:
                self.model=genai.GenerativeModel(model,tools=tools,
                                                 system_instruction=self.system_prompt,
                                                 generation_config=genai.GenerationConfig(
                                                                        max_output_tokens=max_tokens,
                                                                        temperature=temperature,
                                                                    ))
            else:
                self.model=genai.GenerativeModel(model,
                                                 system_instruction=self.system_prompt,
                                                 generation_config=genai.GenerationConfig(
                                                                        max_output_tokens=max_tokens,
                                                                        temperature=temperature,
                                                                    ))
        except:
            print('nope')

    def generate(self,user_msg):
        self.response = self.model.generate_content(user_msg)
        print(self.response.text)
        return self.response.text

    def review_content(self,content):
        self.response = self.model.generate_content(content)
        return self.response.text

    def chat(self,user_msg,auto_funct_call=False):
        print('gemini chat')
        if self.messages is None:
            self.messages=[]
            self.thread=self.model.start_chat(history=self.messages,enable_automatic_function_calling=auto_funct_call)
        self.response=self.thread.send_message([user_msg])
        self.messages.append({'role':'user','content':user_msg})
        self.messages.append({'role':'assistant','content':self.response.text})
        print(self.response.text)
        self.response.text
    
