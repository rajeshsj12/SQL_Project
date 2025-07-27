import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import DatabaseConnection
from utils import format_number, get_table_info
import os

# Page configuration
st.set_page_config(
    page_title="Database Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database connection
@st.cache_resource
def init_database():
    """Initialize database connection with caching"""
    return DatabaseConnection()

def main():
    st.title("📊 Database Explorer Dashboard")
    st.markdown("Welcome to your MySQL database visualization tool")
    
    # Initialize database
    db = init_database()
    
    # Test connection
    if not db.test_connection():
        st.error("❌ Failed to connect to MySQL database. Please check your connection settings.")
        st.info("Make sure your MySQL server is running on localhost and the database 'customersdb' exists.")
        return
    
    st.success("✅ Connected to MySQL database successfully!")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown("---")
    
    # Get all tables
    tables = db.get_all_tables()
    
    if not tables:
        st.error("No tables found in the database.")
        return
    
    # Display overview metrics
    st.header("📈 Database Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tables", len(tables))
    
    with col2:
        total_records = sum([db.get_table_count(table) for table in tables])
        st.metric("Total Records", format_number(total_records))
    
    with col3:
        # Calculate total customers
        customers_count = db.get_table_count('customers')
        st.metric("Customers", format_number(customers_count))
    
    with col4:
        # Calculate total products
        products_count = db.get_table_count('products')
        st.metric("Products", format_number(products_count))
    
    # Table overview
    st.header("📋 Table Overview")
    
    table_data = []
    for table in tables:
        count = db.get_table_count(table)
        columns = db.get_table_columns(table)
        table_data.append({
            'Table': table,
            'Records': count,
            'Columns': len(columns),
            'Primary Key': db.get_primary_key(table)
        })
    
    df_tables = pd.DataFrame(table_data)
    st.dataframe(df_tables, use_container_width=True)
    
    # Quick insights
    st.header("🎯 Quick Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Table sizes chart
        fig = px.bar(
            df_tables, 
            x='Table', 
            y='Records',
            title="Records per Table",
            color='Records',
            color_continuous_scale='viridis'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Table complexity (columns) chart
        fig = px.pie(
            df_tables, 
            values='Columns', 
            names='Table',
            title="Table Complexity (by Columns)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity (if log table exists)
    if 'log' in tables:
        st.header("📝 Recent Activity")
        recent_logs = db.execute_query(
            "SELECT action, changed_by, on_table, time FROM log ORDER BY time DESC LIMIT 10"
        )
        if not recent_logs.empty:
            st.dataframe(recent_logs, use_container_width=True)
        else:
            st.info("No recent activity logged.")
    
    # Navigation instructions
    st.sidebar.markdown("### 🧭 Available Pages")
    st.sidebar.markdown("- **Tables**: Browse and search table data")
    st.sidebar.markdown("- **Analytics**: View charts and trends")
    st.sidebar.markdown("- **Relationships**: Explore table connections")
    st.sidebar.markdown("- **Export**: Download table data")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Database Stats")
    for table in tables[:5]:  # Show first 5 tables
        count = db.get_table_count(table)
        st.sidebar.metric(table.title(), format_number(count))

if __name__ == "__main__":
    main()
