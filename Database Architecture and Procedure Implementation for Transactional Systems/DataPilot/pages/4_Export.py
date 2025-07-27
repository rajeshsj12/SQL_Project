import streamlit as st
import pandas as pd
import io
from datetime import datetime
from database import DatabaseConnection
from utils import format_number, export_to_csv, export_to_excel

st.set_page_config(
    page_title="Export - Database Explorer",
    page_icon="💾",
    layout="wide"
)

def main():
    st.title("💾 Data Export")
    st.markdown("Export your database tables in various formats")
    
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
    
    # Export options
    st.header("🔧 Export Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_table = st.selectbox("Select table to export:", tables)
        export_format = st.selectbox("Export format:", ["CSV", "Excel", "JSON"])
    
    with col2:
        include_headers = st.checkbox("Include column headers", value=True)
        limit_records = st.checkbox("Limit number of records")
        
        if limit_records:
            max_records = st.number_input("Maximum records:", min_value=1, max_value=100000, value=1000)
        else:
            max_records = None
    
    if not selected_table:
        st.info("Please select a table to export")
        return
    
    # Table preview
    st.header(f"📋 Table Preview: {selected_table}")
    
    # Get table info
    table_count = db.get_table_count(selected_table)
    columns_info = db.get_table_columns(selected_table)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", format_number(table_count))
    with col2:
        st.metric("Columns", len(columns_info))
    with col3:
        export_count = min(max_records or table_count, table_count)
        st.metric("Records to Export", format_number(export_count))
    
    # Column selection
    st.subheader("📊 Column Selection")
    
    if columns_info:
        all_columns = [col['Field'] for col in columns_info]
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            select_all = st.checkbox("Select all columns", value=True)
            
            if select_all:
                selected_columns = all_columns
            else:
                selected_columns = st.multiselect(
                    "Choose columns to export:",
                    all_columns,
                    default=all_columns[:5]  # Select first 5 by default
                )
        
        with col2:
            if selected_columns:
                # Show column details
                selected_column_info = [col for col in columns_info if col['Field'] in selected_columns]
                df_columns = pd.DataFrame(selected_column_info)
                st.dataframe(df_columns[['Field', 'Type', 'Null', 'Key']], use_container_width=True)
    
    # Advanced filters
    with st.expander("🔍 Advanced Filters", expanded=False):
        st.write("Apply filters to export specific data subsets")
        
        filter_enabled = st.checkbox("Enable filtering")
        
        if filter_enabled and columns_info:
            filter_column = st.selectbox("Filter by column:", [col['Field'] for col in columns_info])
            filter_operator = st.selectbox("Operator:", ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN"])
            filter_value = st.text_input("Value:")
            
            if filter_column and filter_value:
                st.info(f"Filter: {filter_column} {filter_operator} {filter_value}")
    
    # Preview data
    st.subheader("👀 Data Preview")
    
    # Load preview data
    if selected_columns:
        preview_query = f"SELECT {', '.join([f'`{col}`' for col in selected_columns])} FROM `{selected_table}` LIMIT 10"
        preview_df = db.execute_query(preview_query)
        
        if not preview_df.empty:
            st.dataframe(preview_df, use_container_width=True)
        else:
            st.warning("No data to preview")
    
    # Export section
    st.header("📤 Export Data")
    
    if not selected_columns:
        st.warning("Please select at least one column to export")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Generate Export", type="primary"):
            generate_export(db, selected_table, selected_columns, export_format, 
                          max_records, include_headers, filter_enabled, 
                          locals().get('filter_column'), locals().get('filter_operator'), 
                          locals().get('filter_value'))
    
    with col2:
        if st.button("📊 Export All Tables"):
            export_all_tables(db, tables, export_format)
    
    with col3:
        if st.button("🔄 Export with Relationships"):
            export_with_relationships(db, selected_table, export_format)
    
    # Export history
    st.header("📚 Quick Export Templates")
    
    templates = {
        "Customer Data": {
            "table": "customers",
            "columns": ["customer_id", "first_name", "last_name", "email", "registration_date"],
            "description": "Basic customer information"
        },
        "Order Summary": {
            "table": "orders", 
            "columns": ["order_id", "customer_id", "total_amount", "order_date"],
            "description": "Order summary data"
        },
        "Product Catalog": {
            "table": "products",
            "columns": ["product_id", "product_name", "description", "category_id"],
            "description": "Complete product catalog"
        },
        "Employee Directory": {
            "table": "employees",
            "columns": ["employee_id", "first_name", "last_name", "email", "role"],
            "description": "Employee contact information"
        }
    }
    
    st.subheader("📋 Pre-configured Export Templates")
    
    for template_name, template_config in templates.items():
        if template_config["table"] in tables:
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.write(f"**{template_name}**")
            
            with col2:
                st.write(template_config["description"])
            
            with col3:
                if st.button("Export", key=f"template_{template_name}"):
                    export_template(db, template_config, export_format)

def generate_export(db, table_name, columns, export_format, max_records, include_headers, 
                   filter_enabled, filter_column, filter_operator, filter_value):
    """Generate and download export file"""
    
    try:
        # Build query
        columns_str = ', '.join([f'`{col}`' for col in columns])
        query = f"SELECT {columns_str} FROM `{table_name}`"
        
        # Add filter if enabled
        if filter_enabled and filter_column and filter_value:
            if filter_operator == "IN":
                # Handle IN operator specially
                values = [v.strip() for v in filter_value.split(',')]
                values_str = ', '.join([f"'{v}'" for v in values])
                query += f" WHERE `{filter_column}` IN ({values_str})"
            elif filter_operator == "LIKE":
                query += f" WHERE `{filter_column}` LIKE '%{filter_value}%'"
            else:
                query += f" WHERE `{filter_column}` {filter_operator} '{filter_value}'"
        
        # Add limit if specified
        if max_records:
            query += f" LIMIT {max_records}"
        
        # Execute query
        df = db.execute_query(query)
        
        if df.empty:
            st.error("No data found with the specified criteria")
            return
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{table_name}_export_{timestamp}"
        
        # Export based on format
        if export_format == "CSV":
            csv_data = df.to_csv(index=False, header=include_headers)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"{filename}.csv",
                mime="text/csv"
            )
        
        elif export_format == "Excel":
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=table_name, index=False, header=include_headers)
            
            st.download_button(
                label="📥 Download Excel",
                data=excel_buffer.getvalue(),
                file_name=f"{filename}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        elif export_format == "JSON":
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"{filename}.json",
                mime="application/json"
            )
        
        # Show export summary
        st.success(f"✅ Export ready! {len(df)} records, {len(df.columns)} columns")
        
        # Show file size estimate
        if export_format == "CSV":
            size_mb = len(csv_data.encode('utf-8')) / 1024 / 1024
        elif export_format == "Excel":
            size_mb = len(excel_buffer.getvalue()) / 1024 / 1024
        else:
            size_mb = len(json_data.encode('utf-8')) / 1024 / 1024
        
        st.info(f"📁 File size: {size_mb:.2f} MB")
        
    except Exception as e:
        st.error(f"Export failed: {str(e)}")

def export_all_tables(db, tables, export_format):
    """Export all tables in a single file"""
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if export_format == "Excel":
            # Create Excel file with multiple sheets
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                for table in tables:
                    df = db.get_table_data(table, limit=10000)  # Limit for performance
                    if not df.empty:
                        # Truncate sheet name to 31 characters (Excel limit)
                        sheet_name = table[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            st.download_button(
                label="📥 Download All Tables (Excel)",
                data=excel_buffer.getvalue(),
                file_name=f"all_tables_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        else:
            st.warning("All tables export is only available in Excel format")
            
    except Exception as e:
        st.error(f"Export failed: {str(e)}")

def export_with_relationships(db, table_name, export_format):
    """Export table with related data"""
    
    try:
        # Get foreign key relationships
        relationships = db.get_foreign_keys(table_name)
        
        if not relationships:
            st.warning(f"Table '{table_name}' has no foreign key relationships")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if export_format == "Excel":
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                # Export main table
                main_df = db.get_table_data(table_name, limit=10000)
                main_df.to_excel(writer, sheet_name=table_name, index=False)
                
                # Export related tables
                for rel in relationships:
                    related_table = rel['referenced_table']
                    related_df = db.get_table_data(related_table, limit=10000)
                    if not related_df.empty:
                        sheet_name = related_table[:31]
                        related_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            st.download_button(
                label="📥 Download with Relationships",
                data=excel_buffer.getvalue(),
                file_name=f"{table_name}_with_relationships_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        else:
            st.warning("Relationship export is only available in Excel format")
            
    except Exception as e:
        st.error(f"Export failed: {str(e)}")

def export_template(db, template_config, export_format):
    """Export using predefined template"""
    
    table_name = template_config["table"]
    columns = template_config["columns"]
    
    generate_export(db, table_name, columns, export_format, None, True, 
                   False, None, None, None)

if __name__ == "__main__":
    main()
