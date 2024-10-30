from agents.images import *
import streamlit as st
import os


def list_image_files(directory="local/images/"):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


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