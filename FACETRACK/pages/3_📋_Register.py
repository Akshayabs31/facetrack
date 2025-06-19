import streamlit as st
import pandas as pd
import os
import base64
import pdfkit
from datetime import datetime
from pathlib import Path

# Check if admin is logged in
if not st.session_state.get('admin_logged_in', False):
    st.warning("⚠️ Please login as admin to access this page")
    if st.button("Go to Admin Login"):
        st.session_state.current_page = "0_🔒_Admin.py"
        st.experimental_rerun()
    st.stop()

# Page configuration
st.set_page_config(layout="wide")
st.title("📊 Registration Database")

# File path
REGISTER_FILE = 'register/attendance.csv'

# Custom CSS for the layout
st.markdown("""
<style>
    /* Main container styling */
    .stDataFrame {
        width: 100% !important;
    }
    
    /* Table styling */
    table {
        width: 100% !important;
        table-layout: auto !important;
    }
    
    /* Cell styling */
    th, td {
        padding: 12px 15px !important;
        text-align: left !important;
        white-space: nowrap !important;
        max-width: 300px !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    /* Column specific widths */
    th:nth-child(1), td:nth-child(1) {  /* Name column */
        width: 30% !important;
        min-width: 150px !important;
    }
    th:nth-child(2), td:nth-child(2) {  /* ID column */
        width: 20% !important;
        min-width: 80px !important;
    }
    th:nth-child(3), td:nth-child(3) {  /* Timestamp column */
        width: 30% !important;
        min-width: 180px !important;
    }
    
    /* Search bar styling */
    .search-container {
        margin-bottom: 20px;
    }
    .search-input {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
    }
    
    /* Other styling */
    tr:nth-child(even) {
        background-color: #f8f9fa !important;
    }
    tr:hover {
        background-color: #e9ecef !important;
    }
    .metric {
        border-radius: 0.5rem;
        padding: 1rem;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
        border-left: 4px solid #4e73df;
    }
</style>
""", unsafe_allow_html=True)

def create_download_link(df, file_type):
    """Generate download link for DataFrame"""
    if file_type == "csv":
        data = df.to_csv(index=False)
        b64 = base64.b64encode(data.encode()).decode()
        return f'<a href="data:file/csv;base64,{b64}" download="attendance_report.csv">Download CSV</a>'
    elif file_type == "pdf":
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Attendance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Attendance Report</h1>
            <table>
                <tr>
                    {' '.join(f'<th>{col}</th>' for col in df.columns)}
                </tr>
                {' '.join(
                    f'<tr>{" ".join(f"<td>{value}</td>" for value in row)}</tr>'
                    for row in df.itertuples(index=False)
                )}
            </table>
        </body>
        </html>
        """
        try:
            config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
            pdf = pdfkit.from_string(html, False, configuration=config)
            b64 = base64.b64encode(pdf).decode()
            return f'<a href="data:application/pdf;base64,{b64}" download="attendance_report.pdf">Download PDF</a>'
        except Exception as e:
            st.error(f"PDF generation failed: {str(e)}")
            return ""

def filter_dataframe(df: pd.DataFrame, search_query: str) -> pd.DataFrame:
    """Enhanced filter function to search across all columns"""
    if not search_query:
        return df
    
    search_query = str(search_query).lower()
    mask = pd.Series(False, index=df.index)
    
    # Convert all columns to string and search
    for col in df.columns:
        try:
            # Handle numeric columns (like ID)
            if pd.api.types.is_numeric_dtype(df[col]):
                mask = mask | (df[col].astype(str).str.contains(search_query, case=False))
            # Handle datetime columns (like timestamp)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                mask = mask | (df[col].astype(str).str.contains(search_query, case=False))
            # Handle string columns (like name)
            else:
                mask = mask | (df[col].astype(str).str.lower().str.contains(search_query))
        except:
            continue
            
    return df[mask]

def main():
    # Create register directory if it doesn't exist
    if not os.path.exists('register'):
        os.makedirs('register')
    
    # Check if registration file exists
    if not os.path.exists(REGISTER_FILE):
        st.warning("No registration records found")
        return
    
    # Load registration data
    df = pd.read_csv(REGISTER_FILE)
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    
    # Initialize session state for search queries
    if 'search_all' not in st.session_state:
        st.session_state.search_all = ""
    if 'search_filtered' not in st.session_state:
        st.session_state.search_filtered = ""
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Options")
        
        with st.expander("🔍 Filter Options", expanded=True):
            date_filter = st.date_input("Filter by date")
        
        with st.expander("📤 Export Options", expanded=True):
            export_type = st.radio("Export format:", ["CSV", "PDF"])
            
            # Determine which data to export
            if date_filter:
                data_to_export = filter_dataframe(df[df['date'] == date_filter][['name', 'id', 'timestamp']], 
                                                st.session_state.search_filtered)
                export_label = f" (Filtered: {date_filter})"
            else:
                data_to_export = filter_dataframe(df[['name', 'id', 'timestamp']], 
                                                st.session_state.search_all)
                export_label = " (Current View)"
                
            if st.button(f"Generate Report{export_label}", type="primary"):
                if not data_to_export.empty:
                    if export_type == "CSV":
                        st.markdown(create_download_link(data_to_export, "csv"), unsafe_allow_html=True)
                    else:
                        st.markdown(create_download_link(data_to_export, "pdf"), unsafe_allow_html=True)
                else:
                    st.warning("No data to export!")

    # Main content - two columns layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("📋 All Registration Data")
        
        # Search bar for all data with automatic filtering
        search_all = st.text_input("Search records (name, ID, timestamp):", 
                                 value=st.session_state.search_all,
                                 key="search_all_input",
                                 placeholder="Search across all columns...",
                                 on_change=lambda: setattr(st.session_state, 'search_all', st.session_state.search_all_input))
        
        # Filter data based on search - include all columns in the search
        display_df = filter_dataframe(df[['name', 'id', 'timestamp']], st.session_state.search_all)
        
        # Display dataframe
        st.dataframe(
            display_df,
            height=600
        )
    
    with col2:
        if date_filter:
            st.subheader(f"🔎 Filtered Data ({date_filter})")
            
            # Search bar for filtered data with automatic filtering
            search_filtered = st.text_input("Search filtered records:", 
                                         value=st.session_state.search_filtered,
                                         key="search_filtered_input",
                                         placeholder="Search across all columns...",
                                         on_change=lambda: setattr(st.session_state, 'search_filtered', st.session_state.search_filtered_input))
            
            # Filter data based on date first
            date_filtered_df = df[df['date'] == date_filter]
            
            # Then apply search filter to all columns
            display_filtered_df = filter_dataframe(date_filtered_df[['name', 'id', 'timestamp']], 
                                                st.session_state.search_filtered)
            
            st.dataframe(
                display_filtered_df,
                height=600
            )
        else:
            st.subheader("📈 Summary Statistics")
            
            # Create summary cards using columns
            cols = st.columns(3)
            with cols[0]:
                st.markdown(f"""
                <div class="metric">
                    <h3>Total Registrations</h3>
                    <h2>{len(df):,}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with cols[1]:
                st.markdown(f"""
                <div class="metric">
                    <h3>Unique Names</h3>
                    <h2>{df['name'].nunique()}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with cols[2]:
                st.markdown(f"""
                <div class="metric">
                    <h3>Unique IDs</h3>
                    <h2>{df['id'].nunique()}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Top registrants by count
            st.markdown("**Top Registrants**")
            top_users = df['name'].value_counts().head(5).reset_index()
            top_users.columns = ['Name', 'Count']
            st.dataframe(
                top_users,
                height=200
            )

if __name__ == "__main__":
    main()