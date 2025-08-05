import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database_manager import DatabaseManager
from data_visualizer import DataVisualizer
from query_executor import QueryExecutor
from export_utils import ExportUtils
import os

# Page configuration
st.set_page_config(
    page_title="MySQL Database Manager",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = None
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'current_database' not in st.session_state:
    st.session_state.current_database = None

def main():
    st.title("🗄️ MySQL Database Manager")
    st.markdown("---")
    
    # Sidebar for connection and navigation
    with st.sidebar:
        # Only show connection form if not connected
        if not st.session_state.connected:
            st.header("🔗 Database Connection")
            st.info("📋 First-time setup required")
            
            # Connection form
            with st.form("connection_form"):
                host = st.text_input("Host", value="localhost", disabled=True)
                port = st.number_input("Port", value=3306, disabled=True)
                username = st.text_input("Username", value="root")
                password = st.text_input("Password", type="password", value="password")
                
                connect_btn = st.form_submit_button("🚀 Connect to MySQL", type="primary")
                
                if connect_btn:
                    try:
                        # Create connection string
                        connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/"
                        
                        # Save credentials in session state for future use
                        st.session_state.connection_credentials = {
                            'host': host,
                            'port': port,
                            'username': username,
                            'password': password
                        }
                        
                        # Initialize database manager
                        st.session_state.db_manager = DatabaseManager(connection_string)
                        
                        # Test connection
                        databases = st.session_state.db_manager.get_databases()
                        st.session_state.connected = True
                        st.success("✅ Connected to MySQL!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Connection failed: {str(e)}")
                        st.session_state.connected = False
        else:
            # Show connection status when connected
            st.header("🔗 Connection Status")
            if 'connection_credentials' in st.session_state:
                creds = st.session_state.connection_credentials
                st.success(f"✅ Connected to MySQL")
                st.info(f"📍 {creds['username']}@{creds['host']}:{creds['port']}")
                
                # Disconnect button
                if st.button("🔌 Disconnect", type="secondary"):
                    st.session_state.connected = False
                    st.session_state.db_manager = None
                    st.session_state.current_database = None
                    if 'connection_credentials' in st.session_state:
                        del st.session_state.connection_credentials
                    st.rerun()
        
        # Database selection
        if st.session_state.connected and st.session_state.db_manager:
            st.markdown("---")
            st.header("Database Selection")
            
            try:
                databases = st.session_state.db_manager.get_databases()
                selected_db = st.selectbox(
                    "Select Database:",
                    databases,
                    index=databases.index(st.session_state.current_database) if st.session_state.current_database in databases else 0
                )
                
                if selected_db != st.session_state.current_database:
                    st.session_state.current_database = selected_db
                    st.session_state.db_manager.connect_to_database(selected_db)
                    st.success(f"📂 Connected to database: {selected_db}")
                    st.rerun()
                
            except Exception as e:
                st.error(f"Error loading databases: {str(e)}")
        
        # Navigation with buttons instead of radio
        if st.session_state.connected and st.session_state.current_database:
            st.markdown("---")
            st.header("Navigation")
            
            nav_options = [
                ("📊", "Dashboard"),
                ("📋", "Tables"),
                ("👁️", "Views"), 
                ("⚙️", "Procedures"),
                ("🔧", "Functions"),
                ("⚡", "Triggers"),
                ("💻", "Query Executor"),
                ("📈", "Visualization"),
                ("📤", "Export Data")
            ]
            
            # Initialize selected navigation if not exists
            if 'selected_nav' not in st.session_state:
                st.session_state.selected_nav = "📊 Dashboard"
            
            # Create navigation buttons
            for icon, name in nav_options:
                full_name = f"{icon} {name}"
                if st.button(full_name, key=f"nav_{name}", use_container_width=True):
                    st.session_state.selected_nav = full_name
                    st.rerun()
            
            selected_nav = st.session_state.selected_nav
        else:
            selected_nav = None
    
    # Main content area with right sidebar
    if not st.session_state.connected:
        st.info("👈 Please connect to MySQL database using the sidebar")
        
        # Connection instructions
        st.markdown("## 🔗 Connection Instructions")
        st.markdown("""
        1. **Default Connection**: The application is configured for local MySQL with default credentials
        2. **Username**: root (default)
        3. **Password**: password (default) 
        4. **Host**: localhost (fixed)
        5. **Port**: 3306 (fixed)
        
        **Connection String Format**: `mysql+pymysql://root:password@localhost:3306/database_name`
        """)
        
        # Requirements
        st.markdown("## 📋 Requirements")
        st.markdown("""
        - MySQL server running on localhost:3306
        - Database user with appropriate permissions
        - Required Python packages (see requirements.txt)
        """)
        
    elif not st.session_state.current_database:
        st.info("👈 Please select a database from the sidebar")
        
    else:
        # Create layout with main content and right sidebar
        main_col, sidebar_col = st.columns([3, 1])
        
        with main_col:
            # Main application content based on navigation
            if selected_nav == "📊 Dashboard":
                show_dashboard()
            elif selected_nav == "📋 Tables":
                show_tables()
            elif selected_nav == "👁️ Views":
                show_views()
            elif selected_nav == "⚙️ Procedures":
                show_procedures()
            elif selected_nav == "🔧 Functions":
                show_functions()
            elif selected_nav == "⚡ Triggers":
                show_triggers()
            elif selected_nav == "💻 Query Executor":
                show_query_executor()
            elif selected_nav == "📈 Visualization":
                show_data_visualization()
            elif selected_nav == "📤 Export Data":
                show_export_options()
        
        with sidebar_col:
            # Right sidebar for quick navigation
            st.markdown("### 🔍 Quick Navigation")
            
            try:
                # Get all database objects
                tables = st.session_state.db_manager.get_tables()
                views = st.session_state.db_manager.get_views()
                procedures = st.session_state.db_manager.get_procedures()
                functions = st.session_state.db_manager.get_functions()
                triggers = st.session_state.db_manager.get_triggers()
                
                # Tables section
                if tables:
                    with st.expander(f"📋 Tables ({len(tables)})", expanded=False):
                        for table in tables[:10]:  # Show first 10
                            if st.button(f"📋 {table}", key=f"nav_table_{table}", use_container_width=True):
                                st.session_state.selected_table = table
                                st.session_state.selected_nav = "📋 Tables"
                                st.rerun()
                        if len(tables) > 10:
                            st.caption(f"... +{len(tables)-10} more tables")
                
                # Views section
                if views:
                    with st.expander(f"👁️ Views ({len(views)})", expanded=False):
                        for view in views[:10]:
                            if st.button(f"👁️ {view}", key=f"nav_view_{view}", use_container_width=True):
                                st.session_state.selected_view = view
                                st.session_state.selected_nav = "👁️ Views"  
                                st.rerun()
                        if len(views) > 10:
                            st.caption(f"... +{len(views)-10} more views")
                
                # Procedures section
                if procedures:
                    with st.expander(f"⚙️ Procedures ({len(procedures)})", expanded=False):
                        for proc in procedures[:10]:
                            if st.button(f"⚙️ {proc}", key=f"nav_proc_{proc}", use_container_width=True):
                                st.session_state.selected_procedure = proc
                                st.session_state.selected_nav = "⚙️ Procedures"
                                st.rerun()
                        if len(procedures) > 10:
                            st.caption(f"... +{len(procedures)-10} more procedures")
                
                # Functions section
                if functions:
                    with st.expander(f"🔧 Functions ({len(functions)})", expanded=False):
                        for func in functions[:5]:
                            if st.button(f"🔧 {func}", key=f"nav_func_{func}", use_container_width=True):
                                st.session_state.selected_function = func
                                st.session_state.selected_nav = "🔧 Functions"
                                st.rerun()
                        if len(functions) > 5:
                            st.caption(f"... +{len(functions)-5} more functions")
                
                # Triggers section
                if triggers:
                    with st.expander(f"⚡ Triggers ({len(triggers)})", expanded=False):
                        for trigger in triggers[:5]:
                            if st.button(f"⚡ {trigger}", key=f"nav_trigger_{trigger}", use_container_width=True):
                                st.session_state.selected_trigger = trigger
                                st.session_state.selected_nav = "⚡ Triggers"
                                st.rerun()
                        if len(triggers) > 5:
                            st.caption(f"... +{len(triggers)-5} more triggers")
                            
            except Exception as e:
                st.error(f"Navigation error: {str(e)}")

def show_dashboard():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(f"📊 Database Dashboard - {st.session_state.current_database}")
    with col2:
        if st.button("🔄 Refresh Dashboard", type="secondary"):
            st.rerun()
    
    try:
        # Get database statistics
        tables = st.session_state.db_manager.get_tables()
        views = st.session_state.db_manager.get_views()
        procedures = st.session_state.db_manager.get_procedures()
        functions = st.session_state.db_manager.get_functions()
        triggers = st.session_state.db_manager.get_triggers()
        
        # Database Objects Summary Table
        st.subheader("📊 Database Objects Summary")
        
        # Create summary data
        summary_data = [
            {"Object Type": "📋 Tables", "Count": len(tables), "Description": "Data storage tables"},
            {"Object Type": "👁️ Views", "Count": len(views), "Description": "Virtual tables based on queries"},
            {"Object Type": "⚙️ Procedures", "Count": len(procedures), "Description": "Stored procedures for complex operations"},
            {"Object Type": "🔧 Functions", "Count": len(functions), "Description": "Reusable functions returning values"},
            {"Object Type": "⚡ Triggers", "Count": len(triggers), "Description": "Event-driven database actions"}
        ]
        
        # Display as formatted table
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(
            df_summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Object Type": st.column_config.TextColumn("Object Type", width="medium"),
                "Count": st.column_config.NumberColumn("Count", width="small"),
                "Description": st.column_config.TextColumn("Description", width="large")
            }
        )
        
        st.markdown("---")
        
        # Tables with record counts in table format
        if tables:
            st.subheader("📊 Tables with Record Counts")
            
            table_data = []
            for table in tables:
                try:
                    record_count = st.session_state.db_manager.get_table_row_count(table)
                    table_data.append({
                        "Table Name": table, 
                        "Record Count": record_count,
                        "Status": "✅ Active" if record_count > 0 else "📝 Empty"
                    })
                except Exception as e:
                    table_data.append({
                        "Table Name": table, 
                        "Record Count": "Error",
                        "Status": "❌ Error"
                    })
            
            # Display as formatted table
            if table_data:
                df_records = pd.DataFrame(table_data)
                st.dataframe(
                    df_records,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Table Name": st.column_config.TextColumn("Table Name", width="medium"),
                        "Record Count": st.column_config.NumberColumn("Record Count", width="small"),
                        "Status": st.column_config.TextColumn("Status", width="small")
                    }
                )
                
                # Show summary statistics
                total_records = sum([r["Record Count"] for r in table_data if isinstance(r["Record Count"], int)])
                active_tables = len([r for r in table_data if isinstance(r["Record Count"], int) and r["Record Count"] > 0])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Records", f"{total_records:,}")
                with col2:
                    st.metric("Active Tables", active_tables)
                with col3:
                    st.metric("Empty Tables", len(tables) - active_tables)
            
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")

def show_tables():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(f"📋 Tables in {st.session_state.current_database}")
    with col2:
        if st.button("🔄 Refresh Tables", type="secondary"):
            # Clear selected table to refresh list
            if 'selected_table' in st.session_state:
                del st.session_state.selected_table
            st.rerun()
    
    try:
        tables = st.session_state.db_manager.get_tables()
        
        if tables:
            # Replace dropdown with scrollable button list
            st.markdown("**Select Table:**")
            
            # Create scrollable list with buttons in columns
            table_container = st.container()
            with table_container:
                cols = st.columns(4)
                for i, table in enumerate(tables):
                    with cols[i % 4]:
                        if st.button(f"📋 {table}", key=f"table_{table}", use_container_width=True):
                            st.session_state.selected_table = table
            
            # Show selected table details
            if 'selected_table' in st.session_state and st.session_state.selected_table:
                selected_table = st.session_state.selected_table
                st.markdown("---")
                # Table info tabs
                tab1, tab2, tab3 = st.tabs(["📄 Data", "🔍 Schema", "📊 Info"])
                
                with tab1:
                    st.subheader(f"Data from {selected_table}")
                    
                    # Pagination controls
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        page_size = st.selectbox("Rows per page:", [10, 25, 50, 100], index=1)
                    with col2:
                        page_num = st.number_input("Page:", min_value=1, value=1)
                    
                    # Search functionality
                    search_term = st.text_input("🔍 Search in table:")
                    
                    # Load and display data
                    data = st.session_state.db_manager.get_table_data(
                        selected_table, page_size, page_num, search_term
                    )
                    
                    if not data.empty:
                        st.dataframe(data, use_container_width=True)
                        
                        # Row count
                        total_rows = st.session_state.db_manager.get_table_row_count(selected_table)
                        st.info(f"Total rows: {total_rows}")
                    else:
                        st.info("No data found")
                
                with tab2:
                    st.subheader(f"Schema for {selected_table}")
                    schema = st.session_state.db_manager.get_table_schema(selected_table)
                    if not schema.empty:
                        st.dataframe(schema, use_container_width=True)
                    else:
                        st.info("No schema information available")
                
                with tab3:
                    st.subheader(f"Table Information for {selected_table}")
                    info = st.session_state.db_manager.get_table_info(selected_table)
                    if info:
                        for key, value in info.items():
                            st.text(f"{key}: {value}")
                    else:
                        st.info("No table information available")
        else:
            st.info("No tables found in this database")
            
    except Exception as e:
        st.error(f"Error loading tables: {str(e)}")

def show_views():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(f"👁️ Views in {st.session_state.current_database}")
    with col2:
        if st.button("🔄 Refresh Views", type="secondary"):
            if 'selected_view' in st.session_state:
                del st.session_state.selected_view
            st.rerun()
    
    try:
        views = st.session_state.db_manager.get_views()
        
        if views:
            # Use scrollable container with buttons instead of selectbox
            st.markdown("**Select View:**")
            
            # Create scrollable list with buttons
            view_container = st.container()
            with view_container:
                cols = st.columns(4)
                for i, view in enumerate(views):
                    with cols[i % 4]:
                        if st.button(f"👁️ {view}", key=f"view_{view}", use_container_width=True):
                            st.session_state.selected_view = view
            
            # Show selected view details
            if 'selected_view' in st.session_state and st.session_state.selected_view:
                selected_view = st.session_state.selected_view
                st.markdown("---")
                tab1, tab2 = st.tabs(["📄 Data", "💻 Definition"])
                
                with tab1:
                    st.subheader(f"Data from {selected_view}")
                    data = st.session_state.db_manager.get_view_data(selected_view)
                    if not data.empty:
                        st.dataframe(data, use_container_width=True)
                    else:
                        st.info("No data found")
                
                with tab2:
                    st.subheader(f"View Definition for {selected_view}")
                    definition = st.session_state.db_manager.get_view_definition(selected_view)
                    if definition:
                        st.code(definition, language='sql')
                    else:
                        st.info("No definition available")
        else:
            st.info("No views found in this database")
            
    except Exception as e:
        st.error(f"Error loading views: {str(e)}")

def show_procedures():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(f"⚙️ Stored Procedures in {st.session_state.current_database}")
    with col2:
        if st.button("🔄 Refresh Procedures", type="secondary"):
            if 'selected_procedure' in st.session_state:
                del st.session_state.selected_procedure
            st.rerun()
    
    try:
        procedures = st.session_state.db_manager.get_procedures()
        
        if procedures:
            # Use scrollable container with buttons instead of selectbox
            st.markdown("**Select Procedure:**")
            
            # Create scrollable list with buttons
            procedure_container = st.container()
            with procedure_container:
                cols = st.columns(3)
                for i, procedure in enumerate(procedures):
                    with cols[i % 3]:
                        if st.button(f"📋 {procedure}", key=f"proc_{procedure}", use_container_width=True):
                            st.session_state.selected_procedure = procedure
            
            # Show selected procedure details
            if 'selected_procedure' in st.session_state and st.session_state.selected_procedure:
                selected_procedure = st.session_state.selected_procedure
                st.markdown("---")
                
                tab1, tab2 = st.tabs(["💻 Definition", "▶️ Execute"])
                
                with tab1:
                    st.subheader(f"Procedure Definition for {selected_procedure}")
                    definition = st.session_state.db_manager.get_procedure_definition(selected_procedure)
                    if definition:
                        st.code(definition, language='sql')
                    else:
                        st.info("No definition available")
                
                with tab2:
                    st.subheader(f"Execute {selected_procedure}")
                    
                    # Get procedure parameters
                    params_info = st.session_state.db_manager.get_procedure_parameters(selected_procedure)
                    
                    st.info(f"💡 **Call syntax:** `CALL {selected_procedure}({', '.join(['?' for _ in params_info]) if params_info else ''})`")
                    
                    if params_info:
                        st.markdown("**📝 Parameter Form:**")
                        param_values = []
                        
                        with st.form(f"procedure_form_{selected_procedure}"):
                            param_inputs = {}
                            
                            for i, param in enumerate(params_info):
                                param_name = param.get('parameter_name', f'param_{i}')
                                param_type = param.get('data_type', 'VARCHAR')
                                param_mode = param.get('parameter_mode', 'IN')
                                
                                st.markdown(f"**{param_name}** ({param_type}) - {param_mode}")
                                
                                # Create unique key for each parameter
                                unique_key = f"param_{selected_procedure}_{param_name}_{i}"
                                
                                if 'INT' in param_type.upper():
                                    param_inputs[param_name] = st.number_input(f"Enter {param_name}:", key=unique_key)
                                elif 'DECIMAL' in param_type.upper() or 'FLOAT' in param_type.upper():
                                    param_inputs[param_name] = st.number_input(f"Enter {param_name}:", format="%.2f", key=unique_key)
                                elif 'DATE' in param_type.upper():
                                    param_inputs[param_name] = st.date_input(f"Enter {param_name}:", key=unique_key)
                                else:
                                    param_inputs[param_name] = st.text_input(f"Enter {param_name}:", key=unique_key)
                            
                            execute_btn = st.form_submit_button("🚀 Execute Procedure", type="primary")
                            
                            if execute_btn:
                                try:
                                    # Convert parameter inputs to list in correct order
                                    param_values = [param_inputs.get(param.get('parameter_name', f'param_{i}'), None) 
                                                   for i, param in enumerate(params_info)]
                                    
                                    result = st.session_state.db_manager.execute_procedure(selected_procedure, param_values)
                                    st.success("✅ Procedure executed successfully!")
                                    
                                    if result is not None and not result.empty:
                                        st.subheader("📊 Results:")
                                        st.dataframe(result, use_container_width=True)
                                    else:
                                        st.info("Procedure executed (no results returned)")
                                        
                                except Exception as e:
                                    st.error(f"❌ Error executing procedure: {str(e)}")
                    else:
                        st.warning("⚠️ Be careful when executing stored procedures. They may modify data.")
                        
                        if st.button(f"🚀 Execute {selected_procedure}", type="primary"):
                            try:
                                result = st.session_state.db_manager.execute_procedure(selected_procedure)
                                st.success("✅ Procedure executed successfully!")
                                
                                if result is not None and not result.empty:
                                    st.subheader("📊 Results:")
                                    st.dataframe(result, use_container_width=True)
                                else:
                                    st.info("Procedure executed (no results returned)")
                                    
                            except Exception as e:
                                st.error(f"❌ Error executing procedure: {str(e)}")
        else:
            st.info("No stored procedures found in this database")
            
    except Exception as e:
        st.error(f"Error loading procedures: {str(e)}")

def show_functions():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(f"🔧 Functions in {st.session_state.current_database}")
    with col2:
        if st.button("🔄 Refresh Functions", type="secondary"):
            if 'selected_function' in st.session_state:
                del st.session_state.selected_function
            st.rerun()
    
    try:
        functions = st.session_state.db_manager.get_functions()
        
        if functions:
            # Use scrollable container with buttons instead of selectbox
            st.markdown("**Select Function:**")
            
            # Create scrollable list with buttons
            function_container = st.container()
            with function_container:
                cols = st.columns(3)
                for i, function in enumerate(functions):
                    with cols[i % 3]:
                        if st.button(f"🔧 {function}", key=f"func_{function}", use_container_width=True):
                            st.session_state.selected_function = function
            
            # Show selected function details
            if 'selected_function' in st.session_state and st.session_state.selected_function:
                selected_function = st.session_state.selected_function
                st.markdown("---")
                st.subheader(f"Function Definition for {selected_function}")
                definition = st.session_state.db_manager.get_function_definition(selected_function)
                if definition:
                    st.code(definition, language='sql')
                else:
                    st.info("No definition available")
        else:
            st.info("No functions found in this database")
            
    except Exception as e:
        st.error(f"Error loading functions: {str(e)}")

def show_triggers():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(f"⚡ Triggers in {st.session_state.current_database}")
    with col2:
        if st.button("🔄 Refresh Triggers", type="secondary"):
            if 'selected_trigger' in st.session_state:
                del st.session_state.selected_trigger
            st.rerun()
    
    try:
        triggers = st.session_state.db_manager.get_triggers()
        
        if triggers:
            # Use scrollable container with buttons instead of selectbox
            st.markdown("**Select Trigger:**")
            
            # Create scrollable list with buttons
            trigger_container = st.container()
            with trigger_container:
                cols = st.columns(3)
                for i, trigger in enumerate(triggers):
                    with cols[i % 3]:
                        if st.button(f"⚡ {trigger}", key=f"trig_{trigger}", use_container_width=True):
                            st.session_state.selected_trigger = trigger
            
            # Show selected trigger details
            if 'selected_trigger' in st.session_state and st.session_state.selected_trigger:
                selected_trigger = st.session_state.selected_trigger
                st.markdown("---")
                st.subheader(f"Trigger Definition for {selected_trigger}")
                definition = st.session_state.db_manager.get_trigger_definition(selected_trigger)
                if definition:
                    st.code(definition, language='sql')
                else:
                    st.info("No definition available")
        else:
            st.info("No triggers found in this database")
            
    except Exception as e:
        st.error(f"Error loading triggers: {str(e)}")

def show_query_executor():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("💻 SQL Query Executor")
    with col2:
        if st.button("🔄 Refresh Query Executor", type="secondary"):
            st.rerun()
    
    query_executor = QueryExecutor(st.session_state.db_manager)
    
    # Query input
    query = st.text_area("Enter SQL Query:", height=150, placeholder="SELECT * FROM table_name LIMIT 10;")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        execute_btn = st.button("▶️ Execute Query", type="primary")
    with col2:
        if st.button("📋 Query Examples"):
            examples = [
                "SHOW TABLES;",
                "DESCRIBE table_name;",
                "SELECT * FROM table_name LIMIT 10;",
                "SELECT COUNT(*) FROM table_name;",
                "SHOW PROCESSLIST;"
            ]
            st.info("Example queries:\n" + "\n".join(f"• {ex}" for ex in examples))
    
    if execute_btn and query.strip():
        try:
            result = query_executor.execute_query(query)
            
            if result['success']:
                st.success(f"✅ Query executed successfully! ({result['execution_time']:.3f}s)")
                
                if result['data'] is not None and not result['data'].empty:
                    st.subheader("Query Results:")
                    st.dataframe(result['data'], use_container_width=True)
                    
                    # Export options for query results
                    st.markdown("---")
                    st.subheader("Export Results:")
                    export_utils = ExportUtils()
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        csv_data = export_utils.to_csv(result['data'])
                        st.download_button("📄 Download CSV", csv_data, "query_results.csv", "text/csv")
                    
                    with col2:
                        json_data = export_utils.to_json(result['data'])
                        st.download_button("📄 Download JSON", json_data, "query_results.json", "application/json")
                    
                    with col3:
                        excel_data = export_utils.to_excel(result['data'])
                        st.download_button("📄 Download Excel", excel_data, "query_results.xlsx", 
                                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.info("Query executed successfully (no results returned)")
                    
            else:
                st.error(f"❌ Query failed: {result['error']}")
                
        except Exception as e:
            st.error(f"❌ Error executing query: {str(e)}")

def show_data_visualization():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("📈 Data Visualization")
    with col2:
        if st.button("🔄 Refresh Visualization", type="secondary"):
            st.rerun()
    
    try:
        tables = st.session_state.db_manager.get_tables()
        
        if tables:
            selected_table = st.selectbox("Select Table for Visualization:", tables)
            
            if selected_table:
                # Get table data
                data = st.session_state.db_manager.get_table_data(selected_table, limit=1000)
                
                if not data.empty:
                    visualizer = DataVisualizer(data)
                    
                    # Visualization options
                    viz_type = st.selectbox("Select Visualization Type:", 
                                          ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram", "Box Plot"])
                    
                    # Column selection
                    numeric_columns = data.select_dtypes(include=['int64', 'float64']).columns.tolist()
                    all_columns = data.columns.tolist()
                    
                    if viz_type == "Bar Chart":
                        if len(all_columns) >= 2:
                            x_col = st.selectbox("X-axis:", all_columns)
                            y_col = st.selectbox("Y-axis:", numeric_columns) if numeric_columns else st.selectbox("Y-axis:", all_columns)
                            
                            if st.button("Generate Bar Chart"):
                                fig = visualizer.create_bar_chart(x_col, y_col)
                                st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Line Chart":
                        if len(numeric_columns) >= 2:
                            x_col = st.selectbox("X-axis:", numeric_columns)
                            y_col = st.selectbox("Y-axis:", numeric_columns)
                            
                            if st.button("Generate Line Chart"):
                                fig = visualizer.create_line_chart(x_col, y_col)
                                st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Scatter Plot":
                        if len(numeric_columns) >= 2:
                            x_col = st.selectbox("X-axis:", numeric_columns)
                            y_col = st.selectbox("Y-axis:", numeric_columns)
                            color_col = st.selectbox("Color by (optional):", ["None"] + all_columns)
                            
                            if st.button("Generate Scatter Plot"):
                                color_col = None if color_col == "None" else color_col
                                fig = visualizer.create_scatter_plot(x_col, y_col, color_col)
                                st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Histogram":
                        if numeric_columns:
                            col = st.selectbox("Column:", numeric_columns)
                            bins = st.slider("Number of bins:", 10, 100, 30)
                            
                            if st.button("Generate Histogram"):
                                fig = visualizer.create_histogram(col, bins)
                                st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Box Plot":
                        if numeric_columns:
                            col = st.selectbox("Column:", numeric_columns)
                            
                            if st.button("Generate Box Plot"):
                                fig = visualizer.create_box_plot(col)
                                st.plotly_chart(fig, use_container_width=True)
                    
                    if not numeric_columns:
                        st.warning("No numeric columns found for visualization")
                else:
                    st.info("No data available for visualization")
        else:
            st.info("No tables available for visualization")
            
    except Exception as e:
        st.error(f"Error in data visualization: {str(e)}")

def show_export_options():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("📤 Export Data")
    with col2:
        if st.button("🔄 Refresh Export", type="secondary"):
            st.rerun()
    
    try:
        tables = st.session_state.db_manager.get_tables()
        
        if tables:
            selected_table = st.selectbox("Select Table to Export:", tables)
            
            if selected_table:
                # Export options
                col1, col2 = st.columns(2)
                
                with col1:
                    export_format = st.selectbox("Export Format:", ["CSV", "JSON", "Excel"])
                    limit = st.number_input("Limit rows (0 = all):", min_value=0, value=0)
                
                with col2:
                    include_schema = st.checkbox("Include schema information")
                    compress_data = st.checkbox("Compress data")
                
                if st.button("Generate Export"):
                    try:
                        # Get data
                        data = st.session_state.db_manager.get_table_data(selected_table, limit=limit if limit > 0 else None)
                        
                        if not data.empty:
                            export_utils = ExportUtils()
                            
                            if export_format == "CSV":
                                export_data = export_utils.to_csv(data)
                                filename = f"{selected_table}.csv"
                                mime_type = "text/csv"
                                
                            elif export_format == "JSON":
                                export_data = export_utils.to_json(data)
                                filename = f"{selected_table}.json"
                                mime_type = "application/json"
                                
                            elif export_format == "Excel":
                                export_data = export_utils.to_excel(data)
                                filename = f"{selected_table}.xlsx"
                                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            
                            # Add schema if requested
                            if include_schema:
                                schema = st.session_state.db_manager.get_table_schema(selected_table)
                                st.subheader("Schema Information:")
                                st.dataframe(schema, use_container_width=True)
                            
                            st.success(f"✅ Export ready! ({len(data)} rows)")
                            st.download_button(
                                f"📥 Download {export_format}",
                                export_data,
                                filename,
                                mime_type
                            )
                        else:
                            st.warning("No data to export")
                            
                    except Exception as e:
                        st.error(f"Export failed: {str(e)}")
        else:
            st.info("No tables available for export")
            
    except Exception as e:
        st.error(f"Error in export options: {str(e)}")

if __name__ == "__main__":
    main()
