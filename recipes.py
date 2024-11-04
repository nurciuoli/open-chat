import streamlit as st
from models import model_ids
from utils import *
import json
import os
import pyperclip 

def save_recipe(title, recipe_data):
    """Save recipe to a JSON file"""
    recipes_dir = "local/saved_recipes"
    if not os.path.exists(recipes_dir):
        os.makedirs(recipes_dir)
    
    recipes_file = os.path.join(recipes_dir, "recipes.json")
    
    # Load existing recipes
    if os.path.exists(recipes_file):
        with open(recipes_file, 'r') as f:
            recipes = json.load(f)
    else:
        recipes = {}
    
    # Update with new recipe
    recipes[title] = recipe_data
    
    # Save back to file
    with open(recipes_file, 'w') as f:
        json.dump(recipes, f, indent=4)

def load_recipes():
    """Load all recipes from JSON file"""
    recipes_file = os.path.join("local/saved_recipes", "recipes.json")
    if os.path.exists(recipes_file):
        with open(recipes_file, 'r') as f:
            return json.load(f)
    return {}

def handle_ai_response(section, user_prompt=""):
    """Handle AI response generation and display"""
    current_recipe = st.session_state.current_recipe
    
    # Base system prompts
    base_prompts = {
        'ingredients': "You are a culinary expert. Generate a detailed ingredient list with precise measurements. ONLY include this, do not add any additional chat based messages",
        'instructions': "Your are a cooking instructions generator, you will be given ingredients and instructions and the expected output is 1. a summary with total cooking time 2. step by step instructions",
        'notes': "You are a cooking instructor. Provide helpful tips, variations, and storage information."
    }
    
    # Validation
    if section in ['instructions', 'notes'] and not current_recipe['ingredients'].strip():
        st.warning("Please add ingredients first to get better AI suggestions.", icon="⚠️")
        return
    
    if section == 'notes' and not current_recipe['instructions'].strip():
        st.warning("Please add cooking instructions first to get better AI suggestions.", icon="⚠️")
        return

    initialize_messages()
    st.session_state.agent = initialize_agent(model='llama3.2:1b',system_prompt=base_prompts[section],temperature=.5,max_tokens=1000,tools=None,uploaded_file=None,proj_files=None)
    
    response = generate_response(user_prompt)
    
    # Update content without any formatting
    if current_recipe[section]:
        new_content = current_recipe[section] + "\n\n" + response
    else:
        new_content = response
    
    st.session_state.current_recipe[section] = new_content
    st.rerun()
    

def show_recipes():
    
    if 'current_recipe' not in st.session_state:
        st.session_state.current_recipe = {
            'title': '',
            'ingredients': '',
            'instructions': '',
            'notes': ''
        }
    
    # Load recipes from file
    st.session_state.recipes_list = load_recipes()

     # Main content area
    st.subheader("Recipe Editor", divider="grey")
    title = st.text_input("Recipe Title", value=st.session_state.current_recipe['title'])
    
    # Ingredients Section
    st.subheader("Ingredients")
    col1, col2 = st.columns([3, 2])
    
    with col1:
        tab1, tab2 = st.tabs(["Edit", "Preview"])
        with tab1:
            ingredients = st.text_area("List ingredients here (one per line)", 
                                     value=st.session_state.current_recipe['ingredients'], 
                                     height=200)
        with tab2:
            col_prev1, col_clip1 = st.columns([6,1])
            with col_prev1:
                st.markdown(st.session_state.current_recipe['ingredients'])
            with col_clip1:
                if st.button("📋", key="copy_ingredients", help="Copy ingredients to clipboard"):
                    pyperclip.copy(st.session_state.current_recipe['ingredients'])
                    st.toast("Ingredients copied to clipboard!")
    
    with col2:
        st.markdown("##### AI Help - Ingredients")
        ing_prompt = st.text_area(
            "Add specific instructions for ingredient generation",
            placeholder="E.g., 'Make it vegetarian' or 'Scale for 6 people'",
            key='ing_prompt',
            height=100,
            on_change=lambda: handle_ai_response('ingredients', st.session_state.ing_prompt)
        )
        col2a, col2b = st.columns([3, 2])
        with col2b:
            if st.button('🧂', key='ing_help'):
                handle_ai_response('ingredients', ing_prompt)
    
    # Instructions Section
    st.subheader("Cooking Instructions")
    col3, col4 = st.columns([3, 2])
    
    with col3:
        tab3, tab4 = st.tabs(["Edit", "Preview"])
        with tab3:
            instructions = st.text_area("Write instructions here", 
                                      value=st.session_state.current_recipe['instructions'], 
                                      height=200)
        with tab4:
            col_prev2, col_clip2 = st.columns([6,1])
            with col_prev2:
                st.markdown(st.session_state.current_recipe['instructions'])
            with col_clip2:
                if st.button("📋", key="copy_instructions", help="Copy instructions to clipboard"):
                    pyperclip.copy(st.session_state.current_recipe['instructions'])
                    st.toast("Instructions copied to clipboard!")

    
    
    with col4:
        st.markdown("##### AI Help - Instructions")
        inst_prompt = st.text_area(
            "Add specific instructions for step generation",
            placeholder="E.g., 'Make it simpler' or 'Add more detail about temperatures'",
            key='inst_prompt',
            height=100,
            on_change=lambda: handle_ai_response('instructions', st.session_state.inst_prompt)
        )
        col4a, col4b = st.columns([4, 1])
        with col4b:
            button_disabled = not st.session_state.current_recipe['ingredients'].strip()
            if st.button('👩‍🍳', key='inst_help', disabled=button_disabled):
                handle_ai_response('instructions', inst_prompt)
            if button_disabled:
                st.caption("⚠️ Add ingredients first")
    
    # Notes Section
    st.subheader("Additional Notes")
    col5, col6 = st.columns([3, 2])
    
    with col5:
        tab5, tab6 = st.tabs(["Edit", "Preview"])
        with tab5:
            notes = st.text_area("Additional notes, tips, or variations", 
                               value=st.session_state.current_recipe['notes'], 
                               height=100)
        with tab6:
            col_prev3, col_clip3 = st.columns([6,1])
            with col_prev3:
                st.markdown(st.session_state.current_recipe['notes'])
            with col_clip3:
                if st.button("📋", key="copy_notes", help="Copy notes to clipboard"):
                    pyperclip.copy(st.session_state.current_recipe['notes'])
                    st.toast("Notes copied to clipboard!")
    
    with col6:
        st.markdown("##### AI Help - Notes")
        notes_prompt = st.text_area(
            "Add specific instructions for notes generation",
            placeholder="E.g., 'Focus on storage tips' or 'Suggest variations'",
            key='notes_prompt',
            height=100,
            on_change=lambda: handle_ai_response('notes', st.session_state.notes_prompt)
        )
        col6a, col6b = st.columns([4, 1])
        with col6b:
            button_disabled = not (st.session_state.current_recipe['ingredients'].strip() and 
                                 st.session_state.current_recipe['instructions'].strip())
            if st.button('💡', key='notes_help', disabled=button_disabled):
                handle_ai_response('notes', notes_prompt)
            if button_disabled:
                st.caption("⚠️ Add ingredients and instructions first")

    # Update session state
    st.session_state.current_recipe.update({
        'title': title,
        'ingredients': ingredients,
        'instructions': instructions,
        'notes': notes
    })

    # Save button
    if st.button('💾 Save Recipe', type="primary"):
        if title:
            save_recipe(title, st.session_state.current_recipe.copy())
            st.success(f'Recipe "{title}" saved!', icon="✅")
            load_recipes()
        else:
            st.warning('Please enter a title for the recipe.')

    # Sidebar content (simplified)
    with st.sidebar:
        st.button('📝 New Recipe', 
                 on_click=lambda: setattr(st.session_state, 'current_recipe', 
                                        {'title': '', 'ingredients': '', 'instructions': '', 'notes': ''}), 
                 type="primary", 
                 use_container_width=True)
        
        # Saved Recipes Section
        st.subheader('📚 Saved Recipes')
        show_saved = st.toggle("Show", value=False)
        
        if show_saved:
            saved_recipes = list(st.session_state.recipes_list.keys())
            if saved_recipes:
                selected_recipe = st.selectbox('Select Recipe', saved_recipes, key='selected_recipe')
                if st.button('📂 Load Recipe'):
                    st.session_state.current_recipe = st.session_state.recipes_list[selected_recipe].copy()
                    st.rerun()
        
