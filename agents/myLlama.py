import ollama as o
import base64
#chat func
def chat(user_msg):
    messages = [
    {
        'role': 'user',
        'content': user_msg,
    },
    ]

    response=o.chat('llama3', messages=messages, stream=False)
    return response

#generate func
def generate(prompt,format=None):
    response = o.generate('llama3', prompt, stream=False,format=format)
    return response['response']

#generate with image func
def generate_w_images(prompt,images,stream=True):
    for response in o.generate('llava', prompt, images=images, stream=stream):
        print(response['response'], end='', flush=True)
    print()

# agent class framework
class Agent:
    def __init__(self,model='llama3',system_prompt = 'You are a helpful chat based assistant',
                 max_tokens=8000,temperature=0.5):
        self.system_prompt = system_prompt
        self.max_tokens=max_tokens
        self.temperature = temperature
        self.model=model
        self.response=None
        self.messages=[
    {
        'role': 'system',
        'content': system_prompt,
    },
    ]
    #chat with agent and continue conversation
    def chat(self,user_msg,json_mode=False):
        print('llama chat')


        if json_mode==True:
            out_format='json'
        else:
            out_format=''
        options = {'num_predict':self.max_tokens,
                   'temperature':self.temperature}

        self.messages.append(
        {
            'role': 'user',
            'content': user_msg,
        })
        self.response=o.chat(self.model, messages=self.messages, stream=False,options=options,format=out_format)
        self.messages.append(
        {
            'role': 'assistant',
            'content': self.response['message']['content'],
        })

        return self.response['message']['content']
