# admin_dashboard.py
import streamlit as st
from admin_auth import admin_only
import pickle
import yaml
import os

def admin_dashboard():
    admin_username = admin_only()
    
    st.title(f"Admin Dashboard - Welcome {admin_username}")
    
    # Load configuration
    cfg = yaml.safe_load(open("config.yaml", "r"))
    PKL_PATH = cfg['PATH']["PKL_PATH"]
    
    # Database management section
    st.header("Database Management")
    
    # Load current database
    if os.path.exists(PKL_PATH):
        with open(PKL_PATH, 'rb') as file:
            database = pickle.load(file)
    else:
        database = {}
        st.warning("Database file not found, created new empty database")
    
    # Display current records count
    st.metric("Total Records", len(database))
    
    # Record operations
    with st.expander("Add New Record"):
        with st.form("add_record"):
            record_id = st.number_input("ID", min_value=1)
            name = st.text_input("Name")
            image_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
            submitted = st.form_submit_button("Add Record")
            
            if submitted:
                if image_file is not None:
                    new_record = {
                        'id': record_id,
                        'name': name,
                        'image': image_file.read()
                    }
                    database[len(database)] = new_record
                    with open(PKL_PATH, 'wb') as file:
                        pickle.dump(database, file)
                    st.success("Record added successfully!")
                else:
                    st.error("Please upload an image")
    
    with st.expander("Delete Records"):
        if database:
            record_to_delete = st.selectbox(
                "Select record to delete",
                options=[f"ID: {v['id']} - {v['name']}" for k, v in database.items()],
                key="delete_select"
            )
            if st.button("Delete Record"):
                selected_idx = int(record_to_delete.split(":")[0])
                del database[selected_idx]
                with open(PKL_PATH, 'wb') as file:
                    pickle.dump(database, file)
                st.success("Record deleted successfully!")
                st.experimental_rerun()
        else:
            st.warning("No records to delete")
    
    # Database backup
    st.header("Backup & Restore")
    with st.expander("Backup Database"):
        if os.path.exists(PKL_PATH):
            with open(PKL_PATH, "rb") as file:
                st.download_button(
                    label="Download Database Backup",
                    data=file,
                    file_name="database_backup.pkl",
                    mime="application/octet-stream"
                )
        else:
            st.error("No database file found")
    
    with st.expander("Restore Database"):
        uploaded_file = st.file_uploader("Upload Backup File", type=['pkl'])
        if uploaded_file is not None:
            if st.button("Restore from Backup"):
                with open(PKL_PATH, "wb") as file:
                    file.write(uploaded_file.getbuffer())
                st.success("Database restored successfully!")
                st.experimental_rerun()

if __name__ == "__main__":
    admin_dashboard()