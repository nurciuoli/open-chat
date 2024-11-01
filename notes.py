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

def show_notes():
    if 'current_note' not in st.session_state:
        st.session_state.current_note = {'title': '', 'content': ''}
    
    # Load notes from file instead of session state
    st.session_state.notes_list = load_notes()

    with st.sidebar:
        st.button('New Note', on_click=lambda: setattr(st.session_state, 'current_note', {'title': '', 'content': ''}), type="primary", use_container_width=True)
        
        st.subheader('Saved Notes')
        show_saved = st.toggle("Show", value=False)
        
        if show_saved:
            saved_notes = list(st.session_state.notes_list.keys())
            if saved_notes:
                selected_note = st.selectbox('Select Note', saved_notes, key='selected_note')
                if st.button('Load Note'):
                    st.session_state.current_note = st.session_state.notes_list[selected_note].copy()
                    st.rerun()
        st.subheader('Models and parameters', divider="grey")
        selected_model = st.selectbox('Choose a model', list(model_ids.keys()), key='notes_model', on_change=reset_agent_state)
        
        maxt = model_ids[selected_model]['max']


        ai_actions = st.selectbox("AI Actions", [
            "Generate Content",
            "Summarize",
            "Critic",
            "Custom prompt"
        ])
        if ai_actions == "Custom prompt":

            ai_prompt = st.text_input('System Prompt', value="You are a helpful assistant for note-taking and organizing information", key='notes_system_prompt', on_change=reset_agent_state)
        
        if ai_actions == "Custom prompt" and not ai_prompt:
            st.warning("Please enter a custom prompt.")
        else:
            with st.spinner('AI is thinking...'):
                if ai_actions == "Generate Content":
                    system_prompt = f"Your role is to generate content based on the user's preferences. Do not respond in chat format, only respond with content"
                elif ai_actions == "Summarize":
                    system_prompt = f"Your job is to summarize content. If not additional instructions do just that. Here is the current note:\n\n{st.session_state.current_note}"
                elif ai_actions == "Critic":
                    system_prompt = f"Based on this note, suggest possible areas for improvement:\n\n{st.session_state.current_note}"
                else:
                    system_prompt = ai_prompt
        
        
        temperature = st.slider('Temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01, key='notes_temperature', on_change=reset_agent_state)
        max_length = st.slider('Max Output Length', min_value=32, max_value=maxt, value=1000, step=8, key='notes_max_length', on_change=reset_agent_state)

        initialize_messages()
        
        if "notes_agent" not in st.session_state:
            st.session_state.agent = initialize_agent(
                selected_model, 
                max_length,
                temperature, 
                system_prompt, 
                [], 
                None, 
                None
            )

    st.subheader("Notes Editor", divider="grey")
    
    title = st.text_input("Title", value=st.session_state.current_note['title'])
    content = st.text_area("Content", value=st.session_state.current_note['content'], height=300)
    
    st.session_state.current_note['title'] = title
    st.session_state.current_note['content'] = content

    if st.button('Save Note'):
        if title:
            save_note(title, st.session_state.current_note.copy())
            st.success(f'Note "{title}" saved!', icon="✅")
            load_notes()  # Reload notes after saving
        else:
            st.warning('Please enter a title for the note.')

    st.subheader("AI Assistant", divider="grey")
    
    ai_prompt = st.text_area("Ask AI to help with your notes", height=100)

    if st.button('Get AI Help'):
        response = generate_response(ai_prompt)
        
        # Handle response differently based on AI action
        if ai_actions == "Generate Content":
            # Append generated content to the note
            new_content = content + "\n\n" + response
            st.session_state.current_note['content'] = new_content
            st.rerun()
        else:
            # Display other responses in an expander
            with st.expander("AI Response", expanded=True):
                st.markdown(response)