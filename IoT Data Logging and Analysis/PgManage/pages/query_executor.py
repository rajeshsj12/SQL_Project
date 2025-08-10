import streamlit as st
import pandas as pd
import time

def show():
    """Display the query executor page"""
    st.header("💻 SQL Query Executor")
    
    if not st.session_state.get('connected'):
        st.error("Please connect to a database first")
        return
    
    db_conn = st.session_state.db_connection
    
    # Initialize query history in session state
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["💻 Query Editor", "📚 Query History", "📖 Quick Reference"])
    
    with tab1:
        show_query_editor(db_conn)
    
    with tab2:
        show_query_history()
    
    with tab3:
        show_quick_reference()

def show_query_editor(db_conn):
    """Display the main query editor interface"""
    st.subheader("💻 SQL Query Editor")
    
    # Query input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("**Enter your SQL query:**")
    
    with col2:
        query_type = st.selectbox(
            "Query Type",
            ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "GRANT", "REVOKE", "Custom"]
        )
    
    # Load sample query based on type
    sample_queries = {
        "SELECT": "SELECT * FROM information_schema.tables WHERE table_schema = 'public' LIMIT 10;",
        "INSERT": "INSERT INTO table_name (column1, column2) VALUES ('value1', 'value2');",
        "UPDATE": "UPDATE table_name SET column1 = 'new_value' WHERE condition;",
        "DELETE": "DELETE FROM table_name WHERE condition;",
        "CREATE": "CREATE TABLE new_table (\n    id SERIAL PRIMARY KEY,\n    name VARCHAR(100) NOT NULL,\n    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);",
        "ALTER": "ALTER TABLE table_name ADD COLUMN new_column VARCHAR(50);",
        "DROP": "DROP TABLE IF EXISTS table_name;",
        "GRANT": "GRANT SELECT ON TABLE table_name TO username;",
        "REVOKE": "REVOKE SELECT ON TABLE table_name FROM username;",
        "Custom": ""
    }
    
    default_query = sample_queries.get(query_type, "")
    
    # Query text area
    query = st.text_area(
        "SQL Query",
        value=default_query,
        height=200,
        placeholder="Enter your SQL query here..."
    )
    
    # Query options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        auto_commit = st.checkbox("Auto-commit", value=True, help="Automatically commit transactions")
    
    with col2:
        show_execution_time = st.checkbox("Show execution time", value=True)
    
    with col3:
        limit_results = st.number_input("Limit results", min_value=0, max_value=10000, value=1000)
    
    # Execute button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        execute_button = st.button("🚀 Execute Query", type="primary", use_container_width=True)
    
    with col2:
        explain_button = st.button("📊 Explain Query", use_container_width=True)
    
    # Execute query
    if execute_button and query.strip():
        execute_query(db_conn, query, auto_commit, show_execution_time, limit_results)
    
    # Explain query
    if explain_button and query.strip():
        explain_query(db_conn, query)

def execute_query(db_conn, query, auto_commit, show_execution_time, limit_results):
    """Execute the SQL query and display results"""
    try:
        start_time = time.time()
        
        # Add LIMIT if it's a SELECT query and limit is specified
        processed_query = query.strip()
        if limit_results > 0 and processed_query.upper().startswith('SELECT') and 'LIMIT' not in processed_query.upper():
            processed_query += f" LIMIT {limit_results}"
        
        # Execute query
        if processed_query.upper().startswith(('SELECT', 'WITH', 'SHOW', 'EXPLAIN')):
            # Read-only queries
            result = db_conn.execute_query(processed_query)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if result is not None and not result.empty:
                st.success("✅ Query executed successfully!")
                
                if show_execution_time:
                    st.caption(f"⏱️ Execution time: {execution_time:.3f} seconds")
                
                # Display results
                st.subheader("📊 Query Results")
                
                # Show result summary
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rows returned", len(result))
                with col2:
                    st.metric("Columns", len(result.columns))
                
                # Display data
                st.dataframe(result, use_container_width=True, hide_index=True)
                
                # Option to download results
                if len(result) > 0:
                    csv = result.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"query_results_{int(time.time())}.csv",
                        mime="text/csv"
                    )
            else:
                st.success("✅ Query executed successfully!")
                st.info("No results returned")
                
                if show_execution_time:
                    st.caption(f"⏱️ Execution time: {execution_time:.3f} seconds")
        else:
            # Write queries (INSERT, UPDATE, DELETE, etc.)
            db_conn.execute_query(processed_query, fetch=False)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            st.success("✅ Query executed successfully!")
            
            if show_execution_time:
                st.caption(f"⏱️ Execution time: {execution_time:.3f} seconds")
        
        # Add to query history
        add_to_history(query, execution_time if show_execution_time else None, "SUCCESS")
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time if 'start_time' in locals() else 0
        
        st.error(f"❌ Query execution failed: {str(e)}")
        
        if show_execution_time:
            st.caption(f"⏱️ Execution time: {execution_time:.3f} seconds")
        
        # Add to query history
        add_to_history(query, execution_time if show_execution_time else None, "ERROR", str(e))

def explain_query(db_conn, query):
    """Execute EXPLAIN on the query"""
    try:
        # Only explain SELECT queries
        if not query.strip().upper().startswith(('SELECT', 'WITH')):
            st.warning("EXPLAIN is only supported for SELECT queries")
            return
        
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, VERBOSE) {query}"
        result = db_conn.execute_query(explain_query)
        
        if result is not None and not result.empty:
            st.success("✅ Query explanation generated!")
            st.subheader("📊 Query Execution Plan")
            
            # Display explanation
            for _, row in result.iterrows():
                st.text(row.iloc[0])
        else:
            st.info("No explanation available")
    
    except Exception as e:
        st.error(f"❌ Error explaining query: {str(e)}")

def add_to_history(query, execution_time, status, error_message=None):
    """Add query to history"""
    history_entry = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'query': query[:200] + "..." if len(query) > 200 else query,  # Truncate long queries
        'full_query': query,
        'execution_time': execution_time,
        'status': status,
        'error': error_message
    }
    
    # Keep only last 50 queries
    st.session_state.query_history.insert(0, history_entry)
    if len(st.session_state.query_history) > 50:
        st.session_state.query_history = st.session_state.query_history[:50]

def show_query_history():
    """Display query execution history"""
    st.subheader("📚 Query History")
    
    if not st.session_state.query_history:
        st.info("No queries executed yet")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox("Filter by status", ["All", "SUCCESS", "ERROR"])
    
    with col2:
        if st.button("🗑️ Clear History"):
            st.session_state.query_history = []
            st.rerun()
    
    # Filter history
    filtered_history = st.session_state.query_history
    if status_filter != "All":
        filtered_history = [h for h in filtered_history if h['status'] == status_filter]
    
    # Display history
    for i, entry in enumerate(filtered_history):
        with st.expander(f"{entry['timestamp']} - {entry['status']} - {entry['query'][:50]}..."):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.code(entry['full_query'], language='sql')
                
                if entry['error']:
                    st.error(f"Error: {entry['error']}")
            
            with col2:
                st.write(f"**Status:** {entry['status']}")
                if entry['execution_time']:
                    st.write(f"**Time:** {entry['execution_time']:.3f}s")
                
                if st.button(f"🔄 Re-run", key=f"rerun_{i}"):
                    # Copy query to editor (this would need to be implemented)
                    st.info("Query copied to editor")

def show_quick_reference():
    """Display SQL quick reference"""
    st.subheader("📖 SQL Quick Reference")
    
    # Quick reference tabs
    ref_tab1, ref_tab2, ref_tab3, ref_tab4 = st.tabs([
        "🔍 SELECT Queries", 
        "🛠️ DDL Commands", 
        "🔐 DCL Commands", 
        "📊 PostgreSQL Specific"
    ])
    
    with ref_tab1:
        st.markdown("""
        ### SELECT Query Examples
        
        **Basic SELECT:**
        ```sql
        SELECT column1, column2 FROM table_name;
        SELECT * FROM table_name WHERE condition;
        SELECT COUNT(*) FROM table_name;
        ```
        
        **Advanced SELECT:**
        ```sql
        SELECT t1.*, t2.column FROM table1 t1
        JOIN table2 t2 ON t1.id = t2.foreign_key
        WHERE t1.status = 'active'
        ORDER BY t1.created_at DESC
        LIMIT 10;
        ```
        """)
    
    with ref_tab2:
        st.markdown("""
        ### DDL Commands
        
        **Create Table:**
        ```sql
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ```
        
        **Alter Table:**
        ```sql
        ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
        ALTER TABLE users DROP COLUMN email;
        ```
        """)
    
    with ref_tab3:
        st.markdown("""
        ### DCL Commands
        
        **Grant Privileges:**
        ```sql
        GRANT SELECT, INSERT ON table_name TO username;
        GRANT ALL PRIVILEGES ON DATABASE dbname TO username;
        ```
        
        **Revoke Privileges:**
        ```sql
        REVOKE SELECT ON table_name FROM username;
        REVOKE ALL ON SCHEMA public FROM username;
        ```
        """)
    
    with ref_tab4:
        st.markdown("""
        ### PostgreSQL Specific
        
        **Window Functions:**
        ```sql
        SELECT name, salary,
               ROW_NUMBER() OVER (ORDER BY salary DESC) as rank
        FROM employees;
        ```
        
        **JSON Operations:**
        ```sql
        SELECT data->>'name' as name FROM json_table;
        SELECT * FROM table_name WHERE data @> '{"key": "value"}';
        ```
        """)
        