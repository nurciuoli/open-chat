import streamlit as st
from home import show_home
from chat import show_chat
from images import show_image_generation
from notes import show_notes
from recipes import show_recipes

def main():
    st.set_page_config(page_title="💬 Open-Chat",layout='wide')

    if 'page' not in st.session_state:
        st.session_state.page = 'home'  # Default page

    col1, col2, col3,col4,col5 = st.columns(5)  # Add a new column for the image generation button
    if col1.button("🏠"):
        st.session_state.page = 'home'
    
    if col2.button("🤖"):
        st.session_state.page = 'chat'

    if col3.button("🖼️"):
        st.session_state.page = 'image_generation'
    if col4.button("📝"):  # New notes button
        st.session_state.page = 'notes'
    if col5.button("🍽️"):
        st.session_state.page='recipes'

    if st.session_state.page == 'home':
        show_home()
    elif st.session_state.page == 'image_generation':
        show_image_generation()
    elif st.session_state.page == 'chat':
        show_chat()
    elif st.session_state.page == 'notes':
        show_notes()
    elif st.session_state.page =='recipes':
        show_recipes()

if __name__ == "__main__":
    main()