import streamlit as st
from models import model_ids
from utils import *
import json
import os


def save_note(title, note_data):
    """Save note to a JSON file"""
    notes_dir = "local/saved_notes"
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)
    
    notes_file = os.path.join(notes_dir, "notes.json")
    
    # Load existing notes
    if os.path.exists(notes_file):
        with open(notes_file, 'r') as f:
            notes = json.load(f)
    else:
        notes = {}
    
    # Update with new note
    notes[title] = note_data
    
    # Save back to file
    with open(notes_file, 'w') as f:
        json.dump(notes, f, indent=4)

def load_notes():
    """Load all notes from JSON file"""
    notes_file = os.path.join("local/saved_notes", "notes.json")
    if os.path.exists(notes_file):
        with open(notes_file, 'r') as f:
            return json.load(f)
    return {}

def generate_content():
# Handle AI response in sidebar if not Generate Content
    if st.session_state.get("ai_prompt", ""):
        response = generate_response(st.session_state.user_prompt)
        
        if st.session_state.ai_actions == "Generate Content":
            # Update note content directly
            new_content = st.session_state.current_note['content'] + "\n\n" + response
            st.session_state.current_note['content'] = new_content
            st.rerun()
        else:
            # Show response in sidebar
            with st.expander("AI Response", expanded=True):
                st.markdown(response)
        


def handle_ai_response(user_prompt):
    """Handle AI response generation and display"""
    if user_prompt:
        response = generate_response(user_prompt)
        
        if st.session_state.ai_actions == "Generate Content":
            # Update note content directly
            new_content = st.session_state.current_note['content'] + "\n\n" + response
            st.session_state.current_note['content'] = new_content
            st.rerun()
        else:
            # Show response in sidebar
            with st.sidebar:
                with st.expander("AI Response", expanded=True):
                    st.markdown(response)

def show_notes():
    if 'current_note' not in st.session_state:
        st.session_state.current_note = {'title': '', 'content': ''}
    
    # Load notes from file instead of session state
    st.session_state.notes_list = load_notes()

    # Main content area - just the note editor
    st.subheader("Notes Editor", divider="grey")
    
    title = st.text_input("Title", value=st.session_state.current_note['title'])
    content = st.text_area("Content", value=st.session_state.current_note['content'], height=300)
    
    st.session_state.current_note['title'] = title
    st.session_state.current_note['content'] = content

    if st.button('Save Note'):
        if title:
            save_note(title, st.session_state.current_note.copy())
            st.success(f'Note "{title}" saved!', icon="✅")
            load_notes()
        else:
            st.warning('Please enter a title for the note.')

    # Sidebar content
    with st.sidebar:
        st.button('New Note', 
                 on_click=lambda: setattr(st.session_state, 'current_note', {'title': '', 'content': ''}), 
                 type="primary", 
                 use_container_width=True)
        
        # Saved Notes Section
        st.subheader('Saved Notes')
        show_saved = st.toggle("Show", value=False)
        
        if show_saved:
            saved_notes = list(st.session_state.notes_list.keys())
            if saved_notes:
                selected_note = st.selectbox('Select Note', saved_notes, key='selected_note')
                if st.button('Load Note'):
                    st.session_state.current_note = st.session_state.notes_list[selected_note].copy()
                    st.rerun()

        # AI Section
        st.subheader('Models and parameters', divider="grey")
        selected_model = st.selectbox('Choose a model', 
                                    list(model_ids.keys()), 
                                    key='notes_model', 
                                    on_change=reset_agent_state)
        
        maxt = model_ids[selected_model]['max']

        ai_actions = st.selectbox("AI Actions", [
            "Generate Content",
            "Summarize",
            "Critic",
            "Custom prompt"
        ], key='ai_actions')

        # Handle system prompt based on AI action
        if ai_actions == "Custom prompt":
            system_prompt = st.text_input('System Prompt', 
                                        value="You are a helpful assistant for note-taking and organizing information", 
                                        key='notes_system_prompt', 
                                        on_change=reset_agent_state)
            st.warning("Please enter a custom prompt.")
        else:
            system_prompt = {
                "Generate Content": "Your role is to generate content based on the user's preferences. Do not respond in chat format, only respond with content",
                "Summarize": f"Your job is to summarize content. If not additional instructions do just that. Here is the current note:\n\n{st.session_state.current_note}",
                "Critic": f"Based on this note, suggest possible areas for improvement:\n\n{st.session_state.current_note}"
            }[ai_actions]

        st.session_state.ai_prompt = system_prompt
        
        # Model parameters
        temperature = st.slider('Temperature', 
                              min_value=0.01, 
                              max_value=1.0, 
                              value=0.7, 
                              step=0.01, 
                              key='notes_temperature', 
                              on_change=reset_agent_state)
        
        max_length = st.slider('Max Output Length', 
                             min_value=32, 
                             max_value=maxt, 
                             value=2000, 
                             step=8, 
                             key='notes_max_length', 
                             on_change=reset_agent_state)

        initialize_messages()
        
        if "notes_agent" not in st.session_state:
            st.session_state.agent = initialize_agent(
                selected_model, 
                max_length,
                temperature, 
                st.session_state.ai_prompt, 
                [], 
                None, 
                None
            )

        # AI Assistant Input
        st.subheader("AI Assistant", divider="grey")
        user_prompt = st.text_area("Ask AI to help with your notes", 
                                 height=100, 
                                 key="user_prompt")
        
        # Handle AI response when prompt changes
        if user_prompt:
            handle_ai_response(user_prompt)