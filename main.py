import streamlit as st
from home import show_home
from chat import show_chat
from images import show_image_generation

def main():
    st.set_page_config(page_title="💬 My Chatbot")

    if 'page' not in st.session_state:
        st.session_state.page = 'home'  # Default page

    col1, col2, col3 = st.columns(3)  # Add a new column for the image generation button
    if col1.button("🏠"):
        st.session_state.page = 'home'
    
    if col2.button("🤖"):
        st.session_state.page = 'chat'

    if col3.button("🖼️"):
        st.session_state.page = 'image_generation'

    if st.session_state.page == 'home':
        show_home()
    elif st.session_state.page == 'image_generation':
        show_image_generation()
    elif st.session_state.page == 'chat':
        show_chat()

if __name__ == "__main__":
    main()