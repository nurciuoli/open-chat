import streamlit as st
import os
from agents.myLlama import Agent as LlamaAgent
from agents.myGemini import Agent as GeminiAgent
from agents.myClaude import Agent as ClaudeAgent
from agents.myGpt import Agent as GptAgent,get_file,convert_file_to_png
from models import model_ids
import os
import tempfile
# Define a dictionary mapping model vendors to their respective agent classes
agent_classes = {
    'llama': LlamaAgent,
    'gemini': GeminiAgent,
    'claude': ClaudeAgent,
    'gpt': GptAgent,
}

import base64
from io import BytesIO
from PIL import Image

def display_image(image_data):
    buffered = BytesIO(base64.b64decode(image_data))
    image = Image.open(buffered)
    st.image(image, use_column_width=True)

def initialize_agent(model,max_tokens,temperature,system_prompt,tools,uploaded_file):

    messages = st.session_state.messages[1:-1] if len(st.session_state.messages) > 2 else []
    if st.session_state.selected_tools:
        print(str(st.session_state.selected_tools))
        for tool in st.session_state.selected_tools:
            tools.append({'type':tool})
    
    AgentClass = agent_classes[model_ids[model]['vendor']]
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            files = [temp_file.name]
    else:
        files=None
    return AgentClass(model=model, max_tokens=max_tokens, messages=messages,
                      temperature=temperature, system_prompt=system_prompt, tools=tools, files=files)

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": st.session_state.system_prompt}]
    st.session_state.pop('agent', None)

def reset_agent_state():
    st.session_state.pop('agent', None)

def generate_response(prompt_input):
    st.session_state.agent.chat(prompt_input)
    return st.session_state.agent.messages[-1]['content']

def initialize_messages(system_prompt):
    if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": system_prompt}]


def handle_tool_inout(tool_expander):
    with tool_expander:
        if hasattr(st.session_state.agent, 'tool_input') and hasattr(st.session_state.agent, 'tool_output'):
            if st.session_state.agent.tool_input is not None and st.session_state.agent.tool_output is not None:
                st.subheader("Output")
                for tool_output in st.session_state.agent.tool_output:
                    if 'code_interpreter' in tool_output:
                        code_interpreter_output = tool_output['code_interpreter']
                        for output in code_interpreter_output:
                            if 'image' in output:
                                image_data = output['image']
                                if 'file_id' in image_data:
                                    file_id = image_data['file_id']
                                    file = get_file(file_id)
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                                        temp_file_path = temp_file.name
                                    convert_file_to_png(file.id, temp_file_path)
                                    st.image(temp_file_path)
                                    os.unlink(temp_file_path)  # Delete the temporary file
                                else:
                                    st.write(output)
                            else:
                                st.write(output)
                    else:
                        st.write(tool_output)
                st.subheader("Input")
                for tool_input in st.session_state.agent.tool_input:
                    st.code(tool_input['code_interpreter'], language = 'python')
                    
                


def handle_messages():
    # Main Content Area
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_response(prompt)
                placeholder = st.empty()
                full_response = ''
                for item in response:
                    full_response += item
                    placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)

def main():
    st.set_page_config(page_title="💬 My Chatbot")

    tools=[]

    with st.sidebar:
        st.title('💬 My Chatbot')
        st.write('Fun little chatbot project')
        st.subheader('Models and parameters')
        
        selected_model = st.selectbox('Choose a model', list(model_ids.keys()), key='selected_model', on_change=reset_agent_state)
        tool_select = st.multiselect('Tools', ['code_interpreter'],None,key='selected_tools', on_change=reset_agent_state)
        maxt = model_ids[selected_model]['max']
        
        system_prompt = st.text_input('System Prompt', value="You are a helpful assistant", key='system_prompt',on_change=reset_agent_state)
        temperature = st.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01, key='temperature',on_change=reset_agent_state)
        max_length = st.slider('max_length', min_value=32, max_value=maxt, value=1000, step=8, key='max_length',on_change=reset_agent_state)

        st.button('Clear Chat History', on_click=clear_chat_history)

    uploaded_file = st.file_uploader("Upload a file", type=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv'],on_change=reset_agent_state) 
    
    st.subheader("Chat")

    initialize_messages(system_prompt)
    
    handle_messages()

    if "agent" not in st.session_state:
        st.session_state.agent = initialize_agent(selected_model,max_length,temperature,system_prompt,tools,uploaded_file)
    
    tool_expander = st.expander("Tool Input/Output")
    handle_tool_inout(tool_expander)
        

if __name__ == "__main__":
    main()