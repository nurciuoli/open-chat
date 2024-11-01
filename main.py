import streamlit as st
from home import show_home
from chat import show_chat
from images import show_image_generation
from notes import show_notes

def main():
    st.set_page_config(page_title="💬 My Chatbot")

    if 'page' not in st.session_state:
        st.session_state.page = 'home'  # Default page

    col1, col2, col3,col4 = st.columns(4)  # Add a new column for the image generation button
    if col1.button("🏠"):
        st.session_state.page = 'home'
    
    if col2.button("🤖"):
        st.session_state.page = 'chat'

    if col3.button("🖼️"):
        st.session_state.page = 'image_generation'
    if col4.button("📝"):  # New notes button
        st.session_state.page = 'notes'

    if st.session_state.page == 'home':
        show_home()
    elif st.session_state.page == 'image_generation':
        show_image_generation()
    elif st.session_state.page == 'chat':
        show_chat()
    elif st.session_state.page == 'notes':
        show_notes()

if __name__ == "__main__":
    main()