import streamlit as st
import pandas as pd
from database import DatabaseConnection
from utils import format_number, get_table_info, identify_column_types, create_summary_stats

st.set_page_config(
    page_title="Tables - Database Explorer",
    page_icon="📋",
    layout="wide"
)

def main():
    st.title("📋 Table Browser")
    st.markdown("Browse and explore individual tables")
    
    # Initialize database
    @st.cache_resource
    def init_database():
        return DatabaseConnection()
    
    db = init_database()
    
    if not db.test_connection():
        st.error("❌ Database connection failed")
        return
    
    # Get all tables
    tables = db.get_all_tables()
    
    if not tables:
        st.error("No tables found")
        return
    
    # Sidebar - Table selection
    st.sidebar.title("Table Selection")
    selected_table = st.sidebar.selectbox("Choose a table:", tables)
    
    if not selected_table:
        st.info("Please select a table from the sidebar")
        return
    
    # Display table information
    st.header(f"Table: {selected_table}")
    
    # Get table metadata
    columns_info = db.get_table_columns(selected_table)
    table_count = db.get_table_count(selected_table)
    foreign_keys = db.get_foreign_keys(selected_table)
    
    # Display basic info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", format_number(table_count))
    with col2:
        st.metric("Columns", len(columns_info))
    with col3:
        st.metric("Primary Key", db.get_primary_key(selected_table))
    with col4:
        st.metric("Foreign Keys", len(foreign_keys))
    
    # Table structure
    with st.expander("📋 Table Structure", expanded=False):
        if columns_info:
            df_columns = pd.DataFrame(columns_info)
            st.dataframe(df_columns, use_container_width=True)
        
        if foreign_keys:
            st.subheader("🔗 Foreign Key Relationships")
            for fk in foreign_keys:
                st.write(f"• **{fk['column']}** → {fk['referenced_table']}.{fk['referenced_column']}")
    
    # Search and filters
    st.subheader("🔍 Search and Filter")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("Search in table:", placeholder="Enter search term...")
    
    with col2:
        # Get text columns for search
        text_columns = [col['Field'] for col in columns_info 
                       if any(dtype in col['Type'].lower() for dtype in ['varchar', 'text', 'char'])]
        search_column = st.selectbox("Search in column:", ['All'] + text_columns)
    
    with col3:
        page_size = st.selectbox("Records per page:", [50, 100, 500, 1000], index=1)
    
    # Pagination
    if table_count > 0:
        total_pages = (table_count - 1) // page_size + 1
        page_number = st.number_input("Page:", min_value=1, max_value=total_pages, value=1)
        offset = (page_number - 1) * page_size
        
        st.write(f"Showing page {page_number} of {total_pages} ({format_number(table_count)} total records)")
    else:
        offset = 0
        page_number = 1
    
    # Load and display data
    if search_term:
        # Search data
        if search_column == 'All':
            df = db.search_table(selected_table, search_term)
        else:
            df = db.search_table(selected_table, search_term, search_column)
        
        if df.empty:
            st.warning(f"No records found matching '{search_term}'")
        else:
            st.success(f"Found {len(df)} records matching '{search_term}'")
    else:
        # Regular pagination
        df = db.get_table_data(selected_table, limit=page_size, offset=offset)
    
    # Display data
    if not df.empty:
        st.subheader("📊 Table Data")
        
        # Display options
        col1, col2 = st.columns([1, 1])
        with col1:
            show_index = st.checkbox("Show row numbers", value=True)
        with col2:
            max_width = st.checkbox("Use full width", value=True)
        
        # Display dataframe
        st.dataframe(
            df, 
            use_container_width=max_width,
            hide_index=not show_index
        )
        
        # Summary statistics
        with st.expander("📈 Summary Statistics", expanded=False):
            if len(df) > 0:
                # Column type analysis
                column_types = identify_column_types(df)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Column Types:**")
                    for type_name, cols in column_types.items():
                        if cols:
                            st.write(f"• {type_name.title()}: {len(cols)} columns")
                
                with col2:
                    st.write("**Data Quality:**")
                    null_count = df.isnull().sum().sum()
                    total_cells = df.shape[0] * df.shape[1]
                    completeness = ((total_cells - null_count) / total_cells * 100) if total_cells > 0 else 0
                    st.write(f"• Data Completeness: {completeness:.1f}%")
                    st.write(f"• Null Values: {format_number(null_count)}")
                
                # Detailed statistics
                if st.button("Show Detailed Statistics"):
                    summary_stats = create_summary_stats(df)
                    st.dataframe(summary_stats, use_container_width=True)
    else:
        st.info("No data to display")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Analyze This Table"):
            st.switch_page("pages/2_Analytics.py")
    
    with col2:
        if st.button("🔗 View Relationships"):
            st.switch_page("pages/3_Relationships.py")
    
    with col3:
        if st.button("💾 Export Data"):
            st.switch_page("pages/4_Export.py")

if __name__ == "__main__":
    main()
