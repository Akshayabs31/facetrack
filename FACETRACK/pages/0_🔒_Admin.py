import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import hashlib
import yaml
from pathlib import Path

# Configuration
ADMIN_CONFIG = 'admin_config.yaml'
REGISTER_FILE = 'register/attendance.csv'

# Initialize admin config
def initialize_admin_config():
    if not Path(ADMIN_CONFIG).exists():
        default_config = {
            'admin': {
                'username': 'admin',
                'password': '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'
            }
        }
        with open(ADMIN_CONFIG, 'w') as f:
            yaml.safe_dump(default_config, f)

def verify_admin(username, password):
    try:
        with open(ADMIN_CONFIG, 'r') as f:
            config = yaml.safe_load(f)
        if username == config['admin']['username']:
            hashed_input = hashlib.sha256(password.encode()).hexdigest()
            return hashed_input == config['admin']['password']
    except:
        return False
    return False

def admin_login_page():
    st.title("🔒 Admin Login")
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
    
    if st.session_state.admin_logged_in:
        st.success("Already logged in")
        if st.button("🚪 Logout"):
            st.session_state.admin_logged_in = False
            st.experimental_rerun()
        return True
    
    with st.form("admin_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if verify_admin(username, password):
                st.session_state.admin_logged_in = True
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")
    return st.session_state.admin_logged_in

def load_registration_data():
    """Load and prepare real registration data"""
    try:
        if os.path.exists(REGISTER_FILE):
            df = pd.read_csv(REGISTER_FILE)
            
            # Convert timestamp and ensure proper datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            today = datetime.now().date()
            df['is_today'] = df['date'] == today
            df['is_this_week'] = df['date'] >= (today - timedelta(days=7))
            
            # Sort by date
            df = df.sort_values('timestamp')
            return df
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def create_dashboard():
    """Main dashboard with all requested elements"""
    st.set_page_config(layout="wide")
    st.title("📊 Registration Analytics Dashboard")
    
    # Add logout button at top right
    with st.sidebar:
        if st.button("🚪 Logout"):
            st.session_state.admin_logged_in = False
            st.experimental_rerun()
    
    # Load real data
    df = load_registration_data()
    if df is None or df.empty:
        st.warning("No registration data available")
        return
    
    # Calculate metrics for the 4 boxes
    today = datetime.now().date()
    today_data = df[df['is_today']]
    week_data = df[df['is_this_week']]
    
    total_users = df['id'].nunique()
    today_reg = len(today_data)
    week_reg = len(week_data)
    unique_week_users = week_data['id'].nunique()
    
    # Create the 4 metric boxes
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", total_users)
    with col2:
        st.metric("Today's Check-ins", today_reg)
    with col3:
        st.metric("Weekly Activity", week_reg)
    with col4:
        st.metric("Active This Week", unique_week_users)
    
    # Date range selector
    min_date, max_date = df['date'].min(), df['date'].max()
    st.write("")  # Spacer
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End date", max_date, min_value=min_date, max_value=max_date)
    
    # Filter data based on date range
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    daily_counts = filtered_df.groupby('date').size().reset_index(name='checkins')
    
    # Main line graph with real data
    st.subheader("Daily Registration Activity")
    if not daily_counts.empty:
        fig = px.line(
            daily_counts, 
            x='date', 
            y='checkins',
            title='Actual Daily Registrations',
            labels={'date': 'Date', 'checkins': 'Number of Registrations'},
            markers=True
        )
        
        # Add average line
        avg_checkins = daily_counts['checkins'].mean()
        fig.add_hline(
            y=avg_checkins, 
            line_dash="dash", 
            line_color="green",
            annotation_text=f"Average: {avg_checkins:.1f}",
            annotation_position="bottom right"
        )
        
        # Style the chart
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Date",
            yaxis_title="Registrations",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for selected date range")
    
    # Display raw data in a table
    st.subheader("Registration Details")
    st.dataframe(filtered_df[['name', 'id', 'timestamp']].sort_values('timestamp', ascending=False))

# Main app flow
initialize_admin_config()

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    if admin_login_page():
        st.experimental_rerun()
else:
    create_dashboard()