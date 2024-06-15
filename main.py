import streamlit as st
import os
from agents.myLlama import Agent as LlamaAgent
from agents.myGemini import Agent as GeminiAgent
from agents.myClaude import Agent as ClaudeAgent
from agents.myGpt import Agent as GptAgent
from models import model_ids

# Define a dictionary mapping model vendors to their respective agent classes
agent_classes = {
    'llama': LlamaAgent,
    'gemini': GeminiAgent,
    'claude': ClaudeAgent,
    'gpt': GptAgent,
}

def initialize_agent(model, max_tokens, messages, temperature, system_prompt):
    AgentClass = agent_classes[model_ids[model]['vendor']]
    return AgentClass(model=model, max_tokens=max_tokens, messages=messages,
                      temperature=temperature, system_prompt=system_prompt)

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": st.session_state.system_prompt}]
    st.session_state.pop('agent', None)

def reset_agent_state():
    st.session_state.pop('agent', None)

def generate_response(prompt_input):
    if "agent" not in st.session_state:
        message_history = st.session_state.messages[1:-1] if len(st.session_state.messages) > 2 else []
        st.session_state.agent = initialize_agent(st.session_state.selected_model, st.session_state.max_length,
                                                  message_history, st.session_state.temperature,
                                                  st.session_state.system_prompt)
    st.session_state.agent.chat(prompt_input)
    return st.session_state.agent.messages[-1]['content']

def main():
    st.set_page_config(page_title="💬 My Chatbot")

    with st.sidebar:
        st.title('💬 My Chatbot')
        st.write('Fun little chatbot project')
        st.subheader('Models and parameters')
        
        selected_model = st.selectbox('Choose a model', list(model_ids.keys()), key='selected_model', on_change=reset_agent_state)
        maxt = model_ids[selected_model]['max']
        
        system_prompt = st.text_input('System Prompt', value="You are a helpful assistant", key='system_prompt',on_change=reset_agent_state)
        temperature = st.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01, key='temperature',on_change=reset_agent_state)
        max_length = st.slider('max_length', min_value=32, max_value=maxt, value=1000, step=8, key='max_length',on_change=reset_agent_state)

        st.button('Clear Chat History', on_click=clear_chat_history)

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": system_prompt}]

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
        

if __name__ == "__main__":
    main()