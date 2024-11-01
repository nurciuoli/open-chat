import base64
from io import BytesIO
import streamlit as st
from PIL import Image
from tools import *
import os
import json
import tempfile
from models import model_ids
from agents.myLlama import Agent as LlamaAgent
from agents.myGemini import Agent as GeminiAgent
from agents.myClaude import Agent as ClaudeAgent
from agents.myGrok import Agent as GrokAgent
from agents.myGpt import Agent as GptAgent,get_file,convert_file_to_png
from agents.myPerplexity import Agent as PerplexityAgent
agent_classes = {
    'llama': LlamaAgent,
    'gemini': GeminiAgent,
    'claude': ClaudeAgent,
    'gpt': GptAgent,
    'grok':GrokAgent,
    'perplex':PerplexityAgent,
}

CONFIG_DIR = 'local/'



def handle_tool_inout(directory):
    try:
        if hasattr(st.session_state.agent, 'tool_output'):
            if st.session_state.agent.tool_output is not None:
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
                        #elif 'edit_file' in tool_output:
                        #    st.write(tool_output['edit_file'])
                    else:
                        st.write(tool_output)
        if hasattr(st.session_state.agent, 'tool_input'):
            if st.session_state.agent.tool_input is not None:
                st.subheader("Input")
                file_inputs = [tool_input for tool_input in st.session_state.agent.tool_input if 'write_file' in tool_input]
                
                # Create the directory if it doesn't exist
                os.makedirs(f'sandbox/{directory}', exist_ok=True)

                for file_input in file_inputs:
                    file_name = file_input['write_file']['file_name'] + file_input['write_file']['file_type']
                    with open(os.path.join(f'sandbox/{directory}', file_name), 'w') as f:
                        f.write(file_input['write_file']['content'])
                
                if file_inputs:
                    file_expander = st.expander("Files")
                    with file_expander:
                        # Get the file names
                        file_names = [file_input['write_file']['file_name'] + file_input['write_file']['file_type'] for file_input in file_inputs]
                        # Use file names in the selectbox
                        selected_file_name = st.selectbox('Select a file', file_names)
                        # Get the selected file input
                        selected_file_input = next(file_input for file_input in file_inputs if file_input['write_file']['file_name'] + file_input['write_file']['file_type'] == selected_file_name)
                        print(selected_file_input)
                        st.code(selected_file_input['write_file']['content'], language=selected_file_input['write_file']['file_type'].lstrip('.'))
                for tool_input in st.session_state.agent.tool_input:
                    if 'code_interpreter' in tool_input:
                        st.code(tool_input['code_interpreter'], language = 'python')
                    elif 'write_file' not in tool_input:
                        st.write(tool_input[list(tool_input.keys())[0]])
    except:
        print('no output')
        pass
                


def display_image(image_data):
    buffered = BytesIO(base64.b64decode(image_data))
    image = Image.open(buffered)
    st.image(image, use_column_width=True)

def initialize_agent(model,max_tokens,temperature,system_prompt,tools,uploaded_file,proj_files):
    final_tools=[]
    if model_ids[model]['vendor']=='gpt':
        for tool in tools:
            final_tools.append(gpt_agent_tools[tool])
    elif model_ids[model]['vendor']=='claude':
        for tool in tools:
            final_tools.append(claude_agent_tools[tool])
    elif model_ids[model]['vendor']=='gemini':
        for tool in tools:
            final_tools.append(gemini_agent_tools[tool])

    if hasattr(st.session_state, 'messages'):
        messages = st.session_state.messages[1:-1] if len(st.session_state.messages) > 2 else []
    if hasattr(st.session_state, 'selected_tools'):
        print(str(st.session_state.selected_tools))
        for tool in st.session_state.selected_tools:
            tools.append({'type':tool})
    
    AgentClass = agent_classes[model_ids[model]['vendor']]
    files = []
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            files.append(temp_file.name)
    if proj_files:
        for proj_file in proj_files:
            with open(proj_file, 'rb') as f:
                file_content = f.read()
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_content)
                files.append(temp_file.name)
    return AgentClass(model=model, max_tokens=max_tokens, messages=messages,
                      temperature=temperature, system_prompt=system_prompt, tools=final_tools, files=files)




def clear_chat_history():
    st.session_state.messages = []
    st.session_state.pop('agent', None)

def reset_agent_state():
    st.session_state.pop('agent', None)

def generate_response(prompt_input):
    st.session_state.agent.chat(prompt_input)
    return st.session_state.agent.messages[-1]['content']

def initialize_messages():
    if "messages" not in st.session_state:
            st.session_state.messages = []


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


def save_configuration(config_name, selected_model,system_prompt,temperature,max_length,tools,selected_directory,selected_files):
    config = {
                    'selected_model': selected_model,
                    'system_prompt': system_prompt,
                    'temperature': temperature,
                    'max_length': max_length,
                    'tools': tools,
                    'selected_directory': selected_directory,
                    'selected_files': selected_files
                }
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(os.path.join(CONFIG_DIR, f'{config_name}.json'), 'w') as f:
        json.dump(config, f)

def load_configuration(config_name):
    with open(os.path.join(CONFIG_DIR, f'{config_name}.json'), 'r') as f:
        return json.load(f)

def get_saved_configurations():
    if not os.path.exists(CONFIG_DIR):
        return []
    return [f.split('.')[0] for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]

def load_selected_configuration():
    if 'load_config' in st.session_state:
        config = load_configuration(st.session_state.load_config)
        st.session_state.selected_model = config['selected_model']
        st.session_state.system_prompt = config['system_prompt']
        st.session_state.temperature = config['temperature']
        st.session_state.max_length = config['max_length']
        st.session_state.selected_tools = config['tools']
        st.session_state.selected_directory = config['selected_directory']
        st.session_state.selected_files = config['selected_files']
        del st.session_state.load_config
        st.rerun()

def project_selection():
    project_option = st.radio('Project Option', ['Start New Project', 'Work on Existing'], key='project_option', on_change=reset_agent_state)

    selected_files = []
    if project_option == 'Start New Project':
        new_project_name = st.text_input('New Project Name', value='Untitled', key='new_project_name', on_change=reset_agent_state)
        selected_directory = new_project_name
    else:
        subdirectories = [d for d in os.listdir('sandbox') if os.path.isdir(os.path.join('sandbox', d))]
        selected_directory = st.selectbox('Select a directory', subdirectories, key='selected_directory', on_change=reset_agent_state)
        files_in_directory = os.listdir(f'sandbox/{selected_directory}')
        selected_files = st.multiselect('Select files', files_in_directory, None, key='selected_files', on_change=reset_agent_state)
        selected_files = [os.path.join(f'sandbox/{selected_directory}', file_name) for file_name in selected_files]

    if selected_directory == 'New Project':
        untitled_dirs = [d for d in subdirectories if d.startswith('Untitled')]
        if untitled_dirs:
            max_number = max(int(d.lstrip('Untitled')) for d in untitled_dirs)
            new_number = max_number + 1
        else:
            new_number = 1
        selected_directory = f'Untitled{new_number}'

    return selected_directory, selected_files

    