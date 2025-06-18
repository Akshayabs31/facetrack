# admin_auth.py
import streamlit as st
import hashlib
import yaml

# Load admin credentials from config
cfg = yaml.safe_load(open("config.yaml", "r"))
ADMIN_CREDENTIALS = cfg.get('ADMIN', {})

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def authenticate(username, password):
    if username in ADMIN_CREDENTIALS:
        return check_hashes(password, ADMIN_CREDENTIALS[username])
    return False

def login_widget():
    """Admin login form that returns True if authenticated"""
    login_form = st.sidebar.empty()
    with login_form:
        with st.form("Admin Login"):
            st.markdown("**Admin Login**")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if authenticate(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.success("Login successful")
                    return True
                else:
                    st.error("Invalid credentials")
    return False

def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.experimental_rerun()

def admin_only():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if not st.session_state["authenticated"]:
        if login_widget():
            st.experimental_rerun()
        st.stop()
    else:
        logout_button()
        return st.session_state["username"]