import streamlit as st
import os
from agents.myLlama import Agent as LlamaAgent
from agents.myGemini import Agent as GeminiAgent
from agents.myClaude import Agent as ClaudeAgent
from agents.myGpt import Agent as GptAgent
# App title
from models import model_ids


agent_classes = {
    'llama': LlamaAgent,
    'gemini': GeminiAgent,
    'claude': ClaudeAgent,
    'gpt': GptAgent,
}

st.set_page_config(page_title="💬 My Chatbot")

# Replicate Credentials
with st.sidebar:
    st.title('💬 My Chatbot')
    st.write('Fun little chatbot project')
    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a model', list(model_ids.keys()), key='selected_model',on_change=lambda: st.session_state.pop('agent', None))
    maxt=model_ids[selected_model]['max']
    system_prompt = st.sidebar.text_input('System Prompt', value = "You are a helpful assistant")
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=maxt, value=1000, step=8)


# Function for initializing or re-initializing the agent
def initialize_agent():
    AgentClass = agent_classes[model_ids[selected_model]['vendor']]
    # Exclude the first placeholder message by slicing the list from the second element
    message_history = st.session_state.messages[1:] if len(st.session_state.messages) > 1 else []
    st.session_state.agent = AgentClass(model=selected_model,
                                        max_tokens=max_length,
                                        messages=message_history,
                                        temperature=temperature,
                                        system_prompt=system_prompt)

# Check if the model has been switched and re-initialize the agent if necessary
if 'previous_model' not in st.session_state:
    st.session_state.previous_model = selected_model

if selected_model != st.session_state.previous_model:
    initialize_agent()
    st.session_state.previous_model = selected_model


# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": system_prompt}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    try:
        st.session_state.messages = [{"role": "assistant", "content": system_prompt}]
    
        if "agent" in st.session_state.keys():
            st.session_state.pop('agent')
    except:
        print('failed to clear chat')
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating response
# Function for generating response
def generate_response(prompt_input):
    try:
        if "agent" not in st.session_state.keys():
            AgentClass = agent_classes[model_ids[selected_model]['vendor']]
            try:
                # Exclude the first placeholder message by slicing the list from the second element
                message_history = st.session_state.messages[1:] if len(st.session_state.messages) > 1 else []
                st.session_state.agent = AgentClass(model=selected_model,
                                                    max_tokens=max_length,
                                                    messages=message_history,
                                                    temperature=temperature,
                                                    system_prompt=system_prompt)
            except:
                print('failed to initiate agent')
        st.session_state.agent.chat(prompt_input)
        output = st.session_state.agent.messages[-1]['content']
    except:
        output = 'Sorry please try again'
    
    return f'Assistant: {output}'

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)