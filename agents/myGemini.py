import google.generativeai as genai

import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# agent class framework
class Agent:
    def __init__(self,model='gemini-1.5-pro-latest',system_prompt = 'You are a helpful assistant',tools=None,max_tokens = 8000,temperature = 0.5):
        self.response=None
        self.messages=None
        self.thread=None
        self.model_id=model
        self.max_tokens=max_tokens
        self.temperature=temperature
        self.tools=tools
        self.system_prompt = system_prompt
        self.model=None

    def generate(self,user_msg,json_mode=False):
        if json_mode==True:
            response_type= {"response_mime_type": "application/json"}

        if response_type:
            self.response = self.model.generate_content(user_msg)
        else:
            self.response = self.model.generate_content(user_msg,
                                                    generation_config=response_type)
        print(self.response.text)
        return self.response.text

    def review_content(self,content,json_mode=False):
        self.response = self.model.generate_content(content)
        return self.response.text

    def chat(self,user_msg,json_mode=False,auto_funct_call=False):
        print('gemini chat')

        if json_mode==True:
            response_type= "application/json"
        else:
            response_type= "text/plain"
        try:
            if self.tools is not None:
                self.model=genai.GenerativeModel(self.model_id,tools=self.tools,
                                                 system_instruction=self.system_prompt,
                                                 generation_config=genai.GenerationConfig(
                                                                        max_output_tokens=self.max_tokens,
                                                                        temperature=self.temperature,
                                                                        response_mime_type=response_type,
                                                                    ))
            else:
                self.model=genai.GenerativeModel(self.model_id,
                                                 system_instruction=self.system_prompt,
                                                 generation_config=genai.GenerationConfig(
                                                                        max_output_tokens=self.max_tokens,
                                                                        temperature=self.temperature,
                                                                        response_mime_type=response_type,
                                                                    ))
        except:
            print('nope')

        if self.messages is None:
            self.messages=[]
            self.thread=self.model.start_chat(history=self.messages,enable_automatic_function_calling=auto_funct_call)
        

        if response_type:
            self.response=self.thread.send_message(content=[user_msg])
        else:
            self.response=self.thread.send_message(content=[user_msg],
                                                generation_config=response_type)
        self.messages.append({'role':'user','content':user_msg})
        self.messages.append({'role':'assistant','content':self.response.text})
        print(self.response.text)
        self.response.text
    
