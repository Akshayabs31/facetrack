import streamlit as st
import pickle
import yaml
import numpy as np
from PIL import Image
import io
import os
from pathlib import Path

# Check if admin is logged in
if not st.session_state.get('admin_logged_in', False):
    st.warning("⚠️ Please login as admin to access this page")
    if st.button("Go to Admin Login"):
        st.session_state.current_page = "0_🔒_Admin.py"
        st.experimental_rerun()
    st.stop()

# Load configuration
cfg = yaml.safe_load(open("config.yaml", "r"))
PKL_PATH = cfg['PATH']["PKL_PATH"]
st.set_page_config(layout="wide")

# Session state initialization
if 'last_update' not in st.session_state:
    st.session_state.last_update = 0

# Function to check if database file has changed
def database_modified():
    try:
        return os.path.getmtime(PKL_PATH) > st.session_state.last_update
    except:
        return False

# Load database with update tracking
def load_database():
    try:
        mod_time = os.path.getmtime(PKL_PATH)
        if mod_time > st.session_state.last_update:
            with open(PKL_PATH, 'rb') as file:
                database = pickle.load(file)
            st.session_state.last_update = mod_time
            return database
        return st.session_state.get('database', {})
    except:
        return {}

# Display title
st.title("Face Recognition Database")

# Load current database
database = load_database()
st.session_state.database = database

# Create search box
search_query = st.text_input("Search by name or ID", "")

# Convert image data to displayable format
def process_image(image_data):
    if isinstance(image_data, np.ndarray):
        return Image.fromarray(image_data.astype('uint8'))
    elif isinstance(image_data, bytes):
        return Image.open(io.BytesIO(image_data))
    elif isinstance(image_data, str):  # Assume file path
        try:
            return Image.open(image_data)
        except:
            return None
    return None

# Filter database
filtered_db = {k: v for k, v in database.items() 
              if not search_query or 
              search_query.lower() in str(v['id']).lower() or 
              search_query.lower() in v['name'].lower()}

# Create clean table display
cols = st.columns([0.5, 1, 3, 4])
with cols[0]: st.write("**#**")
with cols[1]: st.write("**ID**")
with cols[2]: st.write("**Name**")
with cols[3]: st.write("**Image**")

for idx, person in filtered_db.items():
    cols = st.columns([0.5, 1, 3, 4])
    with cols[0]:
        st.write(idx)
    with cols[1]:
        st.write(person['id'])
    with cols[2]:
        st.write(person['name'])
    with cols[3]:
        img = process_image(person['image'])
        if img:
            st.image(img, width=150)
        else:
            st.write("Image not available")

# Show record count
st.caption(f"Showing {len(filtered_db)} of {len(database)} records")

# Automatic refresh when database changes
if database_modified():
    st.experimental_rerun()

# Manual refresh button
if st.button("Refresh Database"):
    st.session_state.last_update = 0
    st.experimental_rerun()