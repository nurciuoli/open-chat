import streamlit as st
from models import model_ids
from utils import *
from agents.images import *


def main():
    st.set_page_config(page_title="💬 My Chatbot")

    if 'page' not in st.session_state:
        st.session_state.page = 'home'  # Default page

    col1, col2, col3 = st.columns(3)  # Add a new column for the image generation button
    if col1.button("🏠"):
        st.session_state.page = 'home'
    if col2.button("🖼️"):
        st.session_state.page = 'image_generation'

    if st.session_state.page == 'home':
        show_home()
    elif st.session_state.page == 'image_generation':
        show_image_generation()

def show_home():

    st.subheader("Messages:",divider="grey")
    
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
    
    initialize_messages(system_prompt)

    handle_messages()

    if "agent" not in st.session_state:
        st.session_state.agent = initialize_agent(selected_model, max_length, temperature, system_prompt, tools, uploaded_file, selected_files)

    handle_tool_inout(selected_directory)

def show_image_generation():
    st.subheader("Image Generation")
    with st.sidebar:
        size = st.selectbox("Select image size:", ["256x256", "512x512", "1024x1024"])
        quality = st.selectbox("Select image quality:", ["standard", "high"])
        n = st.slider("Number of images:", 1, 5, 1)
        model = st.selectbox("Select model:", ["dall-e-2", "dall-e-3"])
        
        
        view_saved_images = st.toggle("View Saved Images")

    if view_saved_images:
        # File selection component
        image_files = list_image_files()
        selected_file = st.selectbox("Select an image file:",image_files)
        if selected_file:
            image_path = f"local/images/{selected_file}"
            st.image(image_path, caption="Selected Image")
    else:
        prompt = st.text_input("Enter a prompt for the image:")
        if st.button("Generate Image"):
            if prompt:
                image_url = prompt_image(prompt, size, quality, n, model)
                st.session_state.generated_image_url = image_url  # Store the image URL in session state
            else:
                st.error("Please enter a prompt.")

    if 'generated_image_url' in st.session_state:
        st.image(st.session_state.generated_image_url, caption="Generated Image")
        if st.button("Save Image"):
            st.session_state.show_filename_input = True

        if st.button("Generate New Variation"):
            edited_image_url = generate_variation(st.session_state.generated_image_url, n, size)
            st.image(edited_image_url, caption="Variation")

    if 'show_filename_input' in st.session_state and st.session_state.show_filename_input:
        filename = st.text_input("Enter filename to save the image:", None)
        try:
            if st.button("Confirm Save"):
                if filename:
                    full_filename = "local/images/" + filename
                    archive_image(st.session_state.generated_image_url, full_filename)
                    st.success(f"Image saved as {filename}")
                    del st.session_state.generated_image_url  # Clear the stored image URL after saving
                    del st.session_state.show_filename_input  # Clear the filename input state
                else:
                    st.warning("Please enter a filename to save the image.")
        except:
            st.warning("Save Failed. Please try again.")


if __name__ == "__main__":
    main()