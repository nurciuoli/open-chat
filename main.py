import streamlit as st
from models import model_ids
from utils import *


def main():
    st.set_page_config(page_title="💬 My Chatbot")

    load_selected_configuration()

    with st.sidebar:
        st.button('Clear Chat', on_click=clear_chat_history,type="primary",use_container_width=True)
        st.subheader('Agents')
        with st.expander("Load Saved Agent"):
            saved_configs = get_saved_configurations()
            selected_config = st.selectbox('Select Agent', saved_configs, key='selected_config')
            if st.button('Load Saved Agent'):
                st.session_state.load_config = selected_config
                st.rerun()

        st.subheader('Models and parameters',divider="grey")

        selected_model = st.selectbox('Choose a model', list(model_ids.keys()), key='selected_model', on_change=reset_agent_state)
        tool_select = st.multiselect('Agent Tools', ['write_file', 'edit_file'], None, key='selected_tools', on_change=reset_agent_state)
        on = st.toggle("Code Interpreter", on_change=reset_agent_state)

        tools = ['code_interpreter'] if on else tool_select

        maxt = model_ids[selected_model]['max']

        system_prompt = st.text_input('System Prompt', value="You are a helpful assistant", key='system_prompt', on_change=reset_agent_state)
        temperature = st.slider('Temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01, key='temperature', on_change=reset_agent_state)
        max_length = st.slider('Max Output Length', min_value=32, max_value=maxt, value=1000, step=8, key='max_length', on_change=reset_agent_state)

        uploaded_file = st.file_uploader("Upload a file", type=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv'], on_change=reset_agent_state)

        selected_directory, selected_files = project_selection()

        st.subheader('Agent Management')
        with st.expander("Save Agent"):
            config_name = st.text_input('Agent Name', key='config_name')
            if st.button('Save Agent'):
                save_configuration(config_name, selected_model,system_prompt,temperature,max_length,tools,selected_directory,selected_files)
                st.success(f'Agent "{config_name}" saved!', icon="✅")

    
    st.subheader("Messages:",divider="grey")
    
    initialize_messages(system_prompt)

    handle_messages()

    if "agent" not in st.session_state:
        st.session_state.agent = initialize_agent(selected_model, max_length, temperature, system_prompt, tools, uploaded_file, selected_files)

    handle_tool_inout(selected_directory)

if __name__ == "__main__":
    main()