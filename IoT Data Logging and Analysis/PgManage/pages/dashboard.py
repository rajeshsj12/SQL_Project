import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from database.queries import DASHBOARD_QUERIES, MONITORING_QUERIES
import time

def show():
    """Display the dashboard page"""
    st.header("📊 Database Dashboard")
    
    if not st.session_state.get('connected'):
        st.error("Please connect to a database first")
        return
    
    db_conn = st.session_state.db_connection
    
    # Auto-refresh toggle
    col1, col2 = st.columns([3, 1])
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", key="dashboard_auto_refresh")
    
    if auto_refresh:
        # Auto-refresh every 30 seconds
        time.sleep(30)
        st.rerun()
    
    # Main dashboard content
    show_overview_metrics(db_conn)
    show_database_statistics(db_conn)
    show_table_analytics(db_conn)
    show_performance_metrics(db_conn)

def show_overview_metrics(db_conn):
    """Display overview metrics cards"""
    st.subheader("📈 Overview Metrics")
    
    try:
        # Get counts for different database objects
        table_count = db_conn.execute_query(DASHBOARD_QUERIES['table_count']).iloc[0, 0]
        view_count = db_conn.execute_query(DASHBOARD_QUERIES['view_count']).iloc[0, 0]
        function_count = db_conn.execute_query(DASHBOARD_QUERIES['function_count']).iloc[0, 0]
        procedure_count = db_conn.execute_query(DASHBOARD_QUERIES['procedure_count']).iloc[0, 0]
        trigger_count = db_conn.execute_query(DASHBOARD_QUERIES['trigger_count']).iloc[0, 0]
        index_count = db_conn.execute_query(DASHBOARD_QUERIES['index_count']).iloc[0, 0]
        
        # Database size and connections
        db_size = db_conn.get_database_size()
        active_connections = db_conn.get_active_connections()
        
        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🗂️ Tables", table_count)
            st.metric("👁️ Views", view_count)
        
        with col2:
            st.metric("⚙️ Functions", function_count)
            st.metric("🔧 Procedures", procedure_count)
        
        with col3:
            st.metric("⚡ Triggers", trigger_count)
            st.metric("🗂️ Indexes", index_count)
        
        with col4:
            st.metric("💾 Database Size", db_size)
            st.metric("🔗 Active Connections", active_connections)
        
    except Exception as e:
        st.error(f"Error loading overview metrics: {str(e)}")

def show_database_statistics(db_conn):
    """Display database statistics and charts"""
    st.subheader("📊 Database Statistics")
    
    try:
        # Get database statistics
        db_stats = db_conn.execute_query(MONITORING_QUERIES['database_stats'])
        
        if not db_stats.empty:
            stats = db_stats.iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Transaction statistics
                fig_tx = go.Figure(data=[
                    go.Bar(name='Commits', x=['Transactions'], y=[stats['commits']]),
                    go.Bar(name='Rollbacks', x=['Transactions'], y=[stats['rollbacks']])
                ])
                fig_tx.update_layout(
                    title='Transaction Statistics',
                    barmode='group',
                    height=300
                )
                st.plotly_chart(fig_tx, use_container_width=True)
            
            with col2:
                # Block statistics
                hit_ratio = (stats['blocks_hit'] / (stats['blocks_hit'] + stats['blocks_read']) * 100) if (stats['blocks_hit'] + stats['blocks_read']) > 0 else 0
                
                fig_cache = go.Figure(data=[
                    go.Pie(labels=['Cache Hits', 'Disk Reads'], 
                          values=[stats['blocks_hit'], stats['blocks_read']])
                ])
                fig_cache.update_layout(
                    title=f'Cache Hit Ratio: {hit_ratio:.1f}%',
                    height=300
                )
                st.plotly_chart(fig_cache, use_container_width=True)
            
            # Tuple operations
            col3, col4 = st.columns(2)
            
            with col3:
                st.metric("📤 Tuples Returned", f"{stats['tuples_returned']:,}")
                st.metric("📥 Tuples Fetched", f"{stats['tuples_fetched']:,}")
            
            with col4:
                st.metric("➕ Tuples Inserted", f"{stats['tuples_inserted']:,}")
                st.metric("✏️ Tuples Updated", f"{stats['tuples_updated']:,}")
                st.metric("🗑️ Tuples Deleted", f"{stats['tuples_deleted']:,}")
        
    except Exception as e:
        st.error(f"Error loading database statistics: {str(e)}")

def show_table_analytics(db_conn):
    """Display table analytics and row counts"""
    st.subheader("🗂️ Table Analytics")
    
    try:
        # Get table information
        tables_df = db_conn.get_table_info()
        
        if not tables_df.empty:
            # Add row counts
            row_counts = []
            for _, table in tables_df.iterrows():
                count = db_conn.get_table_row_count(table['schemaname'], table['tablename'])
                row_counts.append(count)
            
            tables_df['row_count'] = row_counts
            
            # Display table with row counts
            st.dataframe(
                tables_df[['schemaname', 'tablename', 'row_count', 'hasindexes', 'hastriggers']],
                column_config={
                    'schemaname': 'Schema',
                    'tablename': 'Table Name',
                    'row_count': st.column_config.NumberColumn('Row Count', format="%d"),
                    'hasindexes': 'Has Indexes',
                    'hastriggers': 'Has Triggers'
                },
                use_container_width=True
            )
            
            # Row count visualization
            if len(tables_df) > 0:
                top_tables = tables_df.nlargest(10, 'row_count')
                
                if not top_tables.empty:
                    fig_rows = px.bar(
                        top_tables,
                        x='tablename',
                        y='row_count',
                        title='Top 10 Tables by Row Count',
                        labels={'row_count': 'Row Count', 'tablename': 'Table Name'}
                    )
                    fig_rows.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_rows, use_container_width=True)
        else:
            st.info("No tables found in the current database")
        
    except Exception as e:
        st.error(f"Error loading table analytics: {str(e)}")

def show_performance_metrics(db_conn):
    """Display performance metrics and monitoring data"""
    st.subheader("⚡ Performance Metrics")
    
    try:
        # Active queries
        active_queries = db_conn.execute_query(MONITORING_QUERIES['active_queries'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🔄 Active Queries**")
            if not active_queries.empty:
                st.dataframe(
                    active_queries[['usename', 'state', 'query_start']],
                    column_config={
                        'usename': 'User',
                        'state': 'State',
                        'query_start': 'Started'
                    },
                    use_container_width=True
                )
            else:
                st.info("No active queries")
        
        with col2:
            # Table statistics
            table_stats = db_conn.execute_query(MONITORING_QUERIES['table_stats'])
            
            st.write("**📊 Table Activity Summary**")
            if not table_stats.empty:
                total_inserts = table_stats['inserts'].sum()
                total_updates = table_stats['updates'].sum()
                total_deletes = table_stats['deletes'].sum()
                
                st.metric("Total Inserts", f"{total_inserts:,}")
                st.metric("Total Updates", f"{total_updates:,}")
                st.metric("Total Deletes", f"{total_deletes:,}")
            else:
                st.info("No table statistics available")
        
        # Index usage statistics
        st.write("**🗂️ Index Usage Statistics**")
        index_usage = db_conn.execute_query(MONITORING_QUERIES['index_usage'])
        
        if not index_usage.empty:
            # Show top used indexes
            top_indexes = index_usage.nlargest(10, 'tuples_read')
            
            if not top_indexes.empty:
                fig_idx = px.bar(
                    top_indexes,
                    x='indexname',
                    y='tuples_read',
                    title='Top 10 Most Used Indexes',
                    labels={'tuples_read': 'Tuples Read', 'indexname': 'Index Name'}
                )
                fig_idx.update_xaxes(tickangle=45)
                st.plotly_chart(fig_idx, use_container_width=True)
            
            # Show detailed index usage
            with st.expander("View Detailed Index Usage"):
                st.dataframe(
                    index_usage,
                    column_config={
                        'schemaname': 'Schema',
                        'tablename': 'Table',
                        'indexname': 'Index',
                        'tuples_read': st.column_config.NumberColumn('Tuples Read', format="%d"),
                        'tuples_fetched': st.column_config.NumberColumn('Tuples Fetched', format="%d")
                    },
                    use_container_width=True
                )
        else:
            st.info("No index usage statistics available")
        
    except Exception as e:
        st.error(f"Error loading performance metrics: {str(e)}")
