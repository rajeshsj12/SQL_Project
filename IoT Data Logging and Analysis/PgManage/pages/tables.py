import streamlit as st
import pandas as pd
from database.queries import TABLE_QUERIES

def show():
    """Display the tables page"""
    st.header("🗂️ Tables Management")
    
    if not st.session_state.get('connected'):
        st.error("Please connect to a database first")
        return
    
    db_conn = st.session_state.db_connection
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 All Tables", "🔍 Table Details", "📈 Table Data", "📋 Column Statistics"])
    
    with tab1:
        show_all_tables(db_conn)
    
    with tab2:
        show_table_details(db_conn)
    
    with tab3:
        show_table_data(db_conn)
    
    with tab4:
        show_column_statistics(db_conn)

def show_all_tables(db_conn):
    """Display all tables with their information"""
    st.subheader("📊 All Tables")
    
    try:
        # Get all tables
        tables_df = db_conn.execute_query(TABLE_QUERIES['all_tables'])
        
        if not tables_df.empty:
            # Add row counts
            with st.spinner("Loading table information..."):
                row_counts = []
                for _, table in tables_df.iterrows():
                    try:
                        count = db_conn.get_table_row_count(table['table_schema'], table['table_name'])
                        row_counts.append(count)
                    except:
                        row_counts.append(0)
                
                tables_df['row_count'] = row_counts
            
            # Search functionality
            search_term = st.text_input("🔍 Search tables", placeholder="Enter table name or schema...")
            
            if search_term:
                filtered_df = tables_df[
                    tables_df['table_name'].str.contains(search_term, case=False, na=False) |
                    tables_df['table_schema'].str.contains(search_term, case=False, na=False)
                ]
            else:
                filtered_df = tables_df
            
            # Display tables
            st.dataframe(
                filtered_df,
                column_config={
                    'table_schema': 'Schema',
                    'table_name': 'Table Name',
                    'table_type': 'Type',
                    'column_count': st.column_config.NumberColumn('Columns', format="%d"),
                    'row_count': st.column_config.NumberColumn('Rows', format="%d"),
                    'size': 'Size'
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Tables", len(filtered_df))
            
            with col2:
                total_rows = filtered_df['row_count'].sum()
                st.metric("Total Rows", f"{total_rows:,}")
            
            with col3:
                avg_columns = filtered_df['column_count'].mean()
                st.metric("Avg Columns", f"{avg_columns:.1f}")
            
            with col4:
                schemas = filtered_df['table_schema'].nunique()
                st.metric("Schemas", schemas)
        else:
            st.info("No tables found in the current database")
    
    except Exception as e:
        st.error(f"Error loading tables: {str(e)}")

def show_table_details(db_conn):
    """Display detailed information about a specific table"""
    st.subheader("🔍 Table Details")
    
    try:
        # Get list of tables for selection
        tables_df = db_conn.execute_query(TABLE_QUERIES['all_tables'])
        
        if not tables_df.empty:
            # Table selection
            table_options = [f"{row['table_schema']}.{row['table_name']}" for _, row in tables_df.iterrows()]
            
            selected_table = st.selectbox("Select a table", table_options)
            
            if selected_table:
                schema, table_name = selected_table.split('.', 1)
                
                # Show table details in tabs
                detail_tab1, detail_tab2, detail_tab3, detail_tab4 = st.tabs([
                    "📋 Columns", "🗂️ Indexes", "🔗 Constraints", "📊 Statistics"
                ])
                
                with detail_tab1:
                    show_table_columns(db_conn, schema, table_name)
                
                with detail_tab2:
                    show_table_indexes(db_conn, schema, table_name)
                
                with detail_tab3:
                    show_table_constraints(db_conn, schema, table_name)
                
                with detail_tab4:
                    show_table_statistics(db_conn, schema, table_name)
        else:
            st.info("No tables available")
    
    except Exception as e:
        st.error(f"Error loading table details: {str(e)}")

def show_table_columns(db_conn, schema, table_name):
    """Display table columns information"""
    st.write(f"**Columns for {schema}.{table_name}**")
    
    try:
        cursor = db_conn.connection.cursor()
        cursor.execute(TABLE_QUERIES['table_columns'], (schema, table_name))
        columns = cursor.fetchall()
        cursor.close()
        
        if columns:
            columns_df = pd.DataFrame(columns, columns=[
                'Column Name', 'Data Type', 'Max Length', 'Nullable', 'Default', 'Position'
            ])
            
            st.dataframe(
                columns_df,
                column_config={
                    'Column Name': 'Column',
                    'Data Type': 'Type',
                    'Max Length': st.column_config.NumberColumn('Length'),
                    'Nullable': 'Null?',
                    'Default': 'Default Value',
                    'Position': st.column_config.NumberColumn('Pos')
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No columns found")
    
    except Exception as e:
        st.error(f"Error loading columns: {str(e)}")

def show_table_indexes(db_conn, schema, table_name):
    """Display table indexes information"""
    st.write(f"**Indexes for {schema}.{table_name}**")
    
    try:
        cursor = db_conn.connection.cursor()
        cursor.execute(TABLE_QUERIES['table_indexes'], (schema, table_name))
        indexes = cursor.fetchall()
        cursor.close()
        
        if indexes:
            for idx_name, idx_def in indexes:
                with st.expander(f"📋 {idx_name}"):
                    st.code(idx_def, language='sql')
        else:
            st.info("No indexes found")
    
    except Exception as e:
        st.error(f"Error loading indexes: {str(e)}")

def show_table_constraints(db_conn, schema, table_name):
    """Display table constraints information"""
    st.write(f"**Constraints for {schema}.{table_name}**")
    
    try:
        cursor = db_conn.connection.cursor()
        cursor.execute(TABLE_QUERIES['table_constraints'], (schema, table_name))
        constraints = cursor.fetchall()
        cursor.close()
        
        if constraints:
            constraints_df = pd.DataFrame(constraints, columns=['Constraint Name', 'Type'])
            
            st.dataframe(
                constraints_df,
                column_config={
                    'Constraint Name': 'Name',
                    'Type': 'Constraint Type'
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No constraints found")
    
    except Exception as e:
        st.error(f"Error loading constraints: {str(e)}")

def show_table_statistics(db_conn, schema, table_name):
    """Display table statistics"""
    st.write(f"**Statistics for {schema}.{table_name}**")
    
    try:
        # Get row count
        row_count = db_conn.get_table_row_count(schema, table_name)
        
        # Get table size
        size_query = f"""
        SELECT pg_size_pretty(pg_total_relation_size('"{schema}"."{table_name}"')) as total_size,
               pg_size_pretty(pg_relation_size('"{schema}"."{table_name}"')) as table_size
        """
        size_result = db_conn.execute_query(size_query)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📊 Row Count", f"{row_count:,}")
            if not size_result.empty:
                st.metric("💾 Table Size", size_result.iloc[0]['table_size'])
        
        with col2:
            if not size_result.empty:
                st.metric("💽 Total Size (with indexes)", size_result.iloc[0]['total_size'])
        
        # Get table statistics from pg_stat_user_tables
        stats_query = f"""
        SELECT 
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze
        FROM pg_stat_user_tables 
        WHERE schemaname = '{schema}' AND tablename = '{table_name}'
        """
        
        stats_result = db_conn.execute_query(stats_query)
        
        if not stats_result.empty:
            stats = stats_result.iloc[0]
            
            st.write("**Activity Statistics:**")
            col3, col4, col5 = st.columns(3)
            
            with col3:
                st.metric("➕ Inserts", f"{stats['inserts']:,}")
                st.metric("✏️ Updates", f"{stats['updates']:,}")
            
            with col4:
                st.metric("🗑️ Deletes", f"{stats['deletes']:,}")
                st.metric("👥 Live Tuples", f"{stats['live_tuples']:,}")
            
            with col5:
                st.metric("💀 Dead Tuples", f"{stats['dead_tuples']:,}")
            
            st.write("**Maintenance Information:**")
            col6, col7 = st.columns(2)
            
            with col6:
                st.write(f"**Last Vacuum:** {stats['last_vacuum'] or 'Never'}")
                st.write(f"**Last Auto Vacuum:** {stats['last_autovacuum'] or 'Never'}")
            
            with col7:
                st.write(f"**Last Analyze:** {stats['last_analyze'] or 'Never'}")
                st.write(f"**Last Auto Analyze:** {stats['last_autoanalyze'] or 'Never'}")
    
    except Exception as e:
        st.error(f"Error loading table statistics: {str(e)}")

def show_table_data(db_conn):
    """Display table data with pagination"""
    st.subheader("📈 Table Data")
    
    try:
        # Get list of tables for selection
        tables_df = db_conn.execute_query(TABLE_QUERIES['all_tables'])
        
        if not tables_df.empty:
            # Table selection
            table_options = [f"{row['table_schema']}.{row['table_name']}" for _, row in tables_df.iterrows()]
            
            selected_table = st.selectbox("Select a table to view data", table_options, key="data_table_select")
            
            if selected_table:
                schema, table_name = selected_table.split('.', 1)
                
                # Pagination controls
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    limit = st.number_input("Rows per page", min_value=10, max_value=1000, value=100, step=10)
                
                with col2:
                    offset = st.number_input("Offset", min_value=0, value=0, step=limit)
                
                with col3:
                    if st.button("🔄 Refresh Data"):
                        st.rerun()
                
                # Query and display data
                try:
                    data_query = f'SELECT * FROM "{schema}"."{table_name}" LIMIT {limit} OFFSET {offset}'
                    data_df = db_conn.execute_query(data_query)
                    
                    if not data_df.empty:
                        st.dataframe(data_df, use_container_width=True, hide_index=True)
                        
                        # Show pagination info
                        total_rows = db_conn.get_table_row_count(schema, table_name)
                        current_start = offset + 1
                        current_end = min(offset + limit, total_rows)
                        
                        st.caption(f"Showing rows {current_start:,} to {current_end:,} of {total_rows:,} total rows")
                    else:
                        st.info("No data found in this table")
                
                except Exception as e:
                    st.error(f"Error loading table data: {str(e)}")
        else:
            st.info("No tables available")
    
    except Exception as e:
        st.error(f"Error loading tables: {str(e)}")

def show_column_statistics(db_conn):
    """Display detailed column statistics for selected table"""
    st.subheader("📋 Column Statistics")
    
    try:
        # Get list of tables for selection
        tables_df = db_conn.execute_query(TABLE_QUERIES['all_tables'])
        
        if not tables_df.empty:
            # Table selection
            table_options = [f"{row['table_schema']}.{row['table_name']}" for _, row in tables_df.iterrows()]
            
            selected_table = st.selectbox("Select a table to analyze", table_options, key="stats_table_select")
            
            if selected_table:
                schema, table_name = selected_table.split('.', 1)
                
                # Get column information
                columns_query = f"""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns
                WHERE table_schema = '{schema}' 
                    AND table_name = '{table_name}'
                ORDER BY ordinal_position
                """
                
                columns_df = db_conn.execute_query(columns_query)
                
                if not columns_df.empty:
                    # Show basic column information
                    st.write("**Column Information:**")
                    st.dataframe(
                        columns_df,
                        column_config={
                            'column_name': 'Column Name',
                            'data_type': 'Data Type',
                            'is_nullable': 'Nullable',
                            'column_default': 'Default Value',
                            'character_maximum_length': 'Max Length',
                            'numeric_precision': 'Precision',
                            'numeric_scale': 'Scale'
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Analyze numeric columns
                    numeric_columns = []
                    text_columns = []
                    
                    for _, col in columns_df.iterrows():
                        if col['data_type'] in ['integer', 'bigint', 'smallint', 'numeric', 'decimal', 'real', 'double precision', 'money']:
                            numeric_columns.append(col['column_name'])
                        elif col['data_type'] in ['character varying', 'varchar', 'character', 'char', 'text']:
                            text_columns.append(col['column_name'])
                    
                    # Show numeric statistics
                    if numeric_columns:
                        st.write("**Numeric Column Statistics:**")
                        
                        for col_name in numeric_columns:
                            with st.expander(f"📊 {col_name} Statistics"):
                                try:
                                    stats_query = f"""
                                    SELECT 
                                        COUNT(*) as total_count,
                                        COUNT("{col_name}") as non_null_count,
                                        COUNT(*) - COUNT("{col_name}") as null_count,
                                        MIN("{col_name}") as min_value,
                                        MAX("{col_name}") as max_value,
                                        AVG("{col_name}") as avg_value,
                                        STDDEV("{col_name}") as std_deviation,
                                        COUNT(DISTINCT "{col_name}") as unique_count
                                    FROM "{schema}"."{table_name}"
                                    """
                                    
                                    stats_result = db_conn.execute_query(stats_query)
                                    
                                    if not stats_result.empty:
                                        stats = stats_result.iloc[0]
                                        
                                        col1, col2, col3, col4 = st.columns(4)
                                        
                                        with col1:
                                            st.metric("Total Count", f"{stats['total_count']:,}")
                                            st.metric("Non-null Count", f"{stats['non_null_count']:,}")
                                        
                                        with col2:
                                            st.metric("Null Count", f"{stats['null_count']:,}")
                                            st.metric("Unique Values", f"{stats['unique_count']:,}")
                                        
                                        with col3:
                                            if stats['min_value'] is not None:
                                                st.metric("Minimum", f"{float(stats['min_value']):.2f}")
                                            if stats['max_value'] is not None:
                                                st.metric("Maximum", f"{float(stats['max_value']):.2f}")
                                        
                                        with col4:
                                            if stats['avg_value'] is not None:
                                                st.metric("Average", f"{float(stats['avg_value']):.2f}")
                                            if stats['std_deviation'] is not None:
                                                st.metric("Std Deviation", f"{float(stats['std_deviation']):.2f}")
                                        
                                        # Calculate percentages
                                        null_percentage = (stats['null_count'] / stats['total_count']) * 100 if stats['total_count'] > 0 else 0
                                        unique_percentage = (stats['unique_count'] / stats['non_null_count']) * 100 if stats['non_null_count'] > 0 else 0
                                        
                                        st.write(f"**Null Percentage:** {null_percentage:.1f}%")
                                        st.write(f"**Uniqueness:** {unique_percentage:.1f}%")
                                
                                except Exception as e:
                                    st.error(f"Error calculating statistics for {col_name}: {str(e)}")
                    
                    # Show text column statistics
                    if text_columns:
                        st.write("**Text Column Statistics:**")
                        
                        for col_name in text_columns:
                            with st.expander(f"📝 {col_name} Statistics"):
                                try:
                                    text_stats_query = f"""
                                    SELECT 
                                        COUNT(*) as total_count,
                                        COUNT("{col_name}") as non_null_count,
                                        COUNT(*) - COUNT("{col_name}") as null_count,
                                        COUNT(DISTINCT "{col_name}") as unique_count,
                                        AVG(LENGTH("{col_name}")) as avg_length,
                                        MIN(LENGTH("{col_name}")) as min_length,
                                        MAX(LENGTH("{col_name}")) as max_length
                                    FROM "{schema}"."{table_name}"
                                    WHERE "{col_name}" IS NOT NULL
                                    """
                                    
                                    text_stats_result = db_conn.execute_query(text_stats_query)
                                    
                                    if not text_stats_result.empty:
                                        text_stats = text_stats_result.iloc[0]
                                        
                                        col1, col2, col3 = st.columns(3)
                                        
                                        with col1:
                                            st.metric("Total Count", f"{text_stats['total_count']:,}")
                                            st.metric("Non-null Count", f"{text_stats['non_null_count']:,}")
                                        
                                        with col2:
                                            st.metric("Null Count", f"{text_stats['null_count']:,}")
                                            st.metric("Unique Values", f"{text_stats['unique_count']:,}")
                                        
                                        with col3:
                                            if text_stats['avg_length'] is not None:
                                                st.metric("Avg Length", f"{float(text_stats['avg_length']):.1f}")
                                            if text_stats['min_length'] is not None and text_stats['max_length'] is not None:
                                                st.metric("Length Range", f"{int(text_stats['min_length'])}-{int(text_stats['max_length'])}")
                                        
                                        # Show most common values
                                        common_values_query = f"""
                                        SELECT "{col_name}" as value, COUNT(*) as frequency
                                        FROM "{schema}"."{table_name}"
                                        WHERE "{col_name}" IS NOT NULL
                                        GROUP BY "{col_name}"
                                        ORDER BY COUNT(*) DESC
                                        LIMIT 10
                                        """
                                        
                                        common_values_result = db_conn.execute_query(common_values_query)
                                        
                                        if not common_values_result.empty:
                                            st.write("**Most Common Values:**")
                                            st.dataframe(
                                                common_values_result,
                                                column_config={
                                                    'value': 'Value',
                                                    'frequency': st.column_config.NumberColumn('Frequency', format="%d")
                                                },
                                                use_container_width=True,
                                                hide_index=True
                                            )
                                
                                except Exception as e:
                                    st.error(f"Error calculating text statistics for {col_name}: {str(e)}")
                    
                    # Summary section
                    st.write("**Column Summary:**")
                    
                    summary_data = {
                        'Category': ['Total Columns', 'Numeric Columns', 'Text Columns', 'Other Columns'],
                        'Count': [
                            len(columns_df),
                            len(numeric_columns),
                            len(text_columns),
                            len(columns_df) - len(numeric_columns) - len(text_columns)
                        ]
                    }
                    
                    summary_df = pd.DataFrame(summary_data)
                    
                    st.dataframe(
                        summary_df,
                        column_config={
                            'Category': 'Column Category',
                            'Count': st.column_config.NumberColumn('Count', format="%d")
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                    
                else:
                    st.info("No column information available for this table")
        else:
            st.info("No tables available")
    
    except Exception as e:
        st.error(f"Error loading column statistics: {str(e)}")
