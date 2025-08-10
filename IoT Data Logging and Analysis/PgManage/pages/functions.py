import streamlit as st
import pandas as pd
from database.queries import FUNCTION_QUERIES

def show():
    """Display the functions page"""
    st.header("⚙️ Functions Management")
    
    if not st.session_state.get('connected'):
        st.error("Please connect to a database first")
        return
    
    db_conn = st.session_state.db_connection
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📊 All Functions", "🔍 Function Details", "▶️ Execute Function"])
    
    with tab1:
        show_all_functions(db_conn)
    
    with tab2:
        show_function_details(db_conn)
    
    with tab3:
        show_function_executor(db_conn)

def show_all_functions(db_conn):
    """Display all functions and procedures"""
    st.subheader("📊 All Functions & Procedures")
    
    try:
        # Get all functions and procedures
        functions_df = db_conn.execute_query(FUNCTION_QUERIES['all_functions'])
        
        if not functions_df.empty:
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                search_term = st.text_input("🔍 Search functions", placeholder="Enter function name or schema...")
            
            with col2:
                routine_types = functions_df['routine_type'].unique()
                selected_type = st.selectbox("Filter by type", ['All'] + list(routine_types))
            
            # Apply filters
            filtered_df = functions_df.copy()
            
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['routine_name'].str.contains(search_term, case=False, na=False) |
                    filtered_df['routine_schema'].str.contains(search_term, case=False, na=False)
                ]
            
            if selected_type != 'All':
                filtered_df = filtered_df[filtered_df['routine_type'] == selected_type]
            
            # Display functions
            st.dataframe(
                filtered_df[['routine_schema', 'routine_name', 'routine_type', 'return_type']],
                column_config={
                    'routine_schema': 'Schema',
                    'routine_name': 'Name',
                    'routine_type': 'Type',
                    'return_type': 'Return Type'
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Functions", len(filtered_df[filtered_df['routine_type'] == 'FUNCTION']))
            
            with col2:
                st.metric("Total Procedures", len(filtered_df[filtered_df['routine_type'] == 'PROCEDURE']))
            
            with col3:
                schemas = filtered_df['routine_schema'].nunique()
                st.metric("Schemas", schemas)
        else:
            st.info("No functions or procedures found in the current database")
    
    except Exception as e:
        st.error(f"Error loading functions: {str(e)}")

def show_function_details(db_conn):
    """Display detailed information about a specific function"""
    st.subheader("🔍 Function Details")
    
    try:
        # Get list of functions for selection
        functions_df = db_conn.execute_query(FUNCTION_QUERIES['all_functions'])
        
        if not functions_df.empty:
            # Function selection
            function_options = [
                f"{row['routine_schema']}.{row['routine_name']} ({row['routine_type']})"
                for _, row in functions_df.iterrows()
            ]
            
            selected_function = st.selectbox("Select a function or procedure", function_options)
            
            if selected_function:
                # Parse selection
                parts = selected_function.split(' (')
                schema_and_name = parts[0]
                routine_type = parts[1].rstrip(')')
                schema, routine_name = schema_and_name.split('.', 1)
                
                # Get function details
                function_row = functions_df[
                    (functions_df['routine_schema'] == schema) &
                    (functions_df['routine_name'] == routine_name) &
                    (functions_df['routine_type'] == routine_type)
                ].iloc[0]
                
                # Display function information
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Schema:** {function_row['routine_schema']}")
                    st.write(f"**Name:** {function_row['routine_name']}")
                    st.write(f"**Type:** {function_row['routine_type']}")
                
                with col2:
                    st.write(f"**Return Type:** {function_row['return_type']}")
                
                # Show parameters
                st.subheader("📋 Parameters")
                show_function_parameters(db_conn, schema, routine_name)
                
                # Show function source code
                st.subheader("📝 Source Code")
                if pd.notna(function_row['routine_definition']):
                    st.code(function_row['routine_definition'], language='sql')
                elif pd.notna(function_row['source_code']):
                    st.code(function_row['source_code'], language='sql')
                else:
                    st.info("Source code not available")
        else:
            st.info("No functions or procedures available")
    
    except Exception as e:
        st.error(f"Error loading function details: {str(e)}")

def show_function_parameters(db_conn, schema, routine_name):
    """Display function parameters"""
    try:
        # Get function parameters using information_schema
        params_query = """
        SELECT 
            parameter_name,
            data_type,
            parameter_mode,
            ordinal_position
        FROM information_schema.parameters 
        WHERE specific_schema = %s AND specific_name = %s
        ORDER BY ordinal_position
        """
        
        cursor = db_conn.connection.cursor()
        cursor.execute(params_query, (schema, routine_name))
        parameters = cursor.fetchall()
        cursor.close()
        
        if parameters:
            params_df = pd.DataFrame(parameters, columns=[
                'Parameter Name', 'Data Type', 'Mode', 'Position'
            ])
            
            st.dataframe(
                params_df,
                column_config={
                    'Parameter Name': 'Name',
                    'Data Type': 'Type',
                    'Mode': 'Mode',
                    'Position': st.column_config.NumberColumn('Pos')
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No parameters found")
    
    except Exception as e:
        st.error(f"Error loading parameters: {str(e)}")

def show_function_executor(db_conn):
    """Display function execution interface"""
    st.subheader("▶️ Execute Function")
    
    try:
        # Get list of functions for selection
        functions_df = db_conn.execute_query(FUNCTION_QUERIES['all_functions'])
        
        if not functions_df.empty:
            # Function selection
            function_options = [
                f"{row['routine_schema']}.{row['routine_name']} ({row['routine_type']})"
                for _, row in functions_df.iterrows()
            ]
            
            selected_function = st.selectbox("Select a function to execute", function_options, key="exec_function_select")
            
            if selected_function:
                # Parse selection
                parts = selected_function.split(' (')
                schema_and_name = parts[0]
                routine_type = parts[1].rstrip(')')
                schema, routine_name = schema_and_name.split('.', 1)
                
                # Get function parameters
                params_query = """
                SELECT 
                    parameter_name,
                    data_type,
                    parameter_mode,
                    ordinal_position
                FROM information_schema.parameters 
                WHERE specific_schema = %s AND specific_name = %s
                AND parameter_mode IN ('IN', 'INOUT')
                ORDER BY ordinal_position
                """
                
                cursor = db_conn.connection.cursor()
                cursor.execute(params_query, (schema, routine_name))
                parameters = cursor.fetchall()
                cursor.close()
                
                # Create input form
                with st.form("function_execution_form"):
                    st.write(f"**Executing:** {schema}.{routine_name}")
                    
                    param_values = {}
                    if parameters:
                        st.write("**Parameters:**")
                        for param_name, data_type, param_mode, position in parameters:
                            if param_name:  # Skip unnamed parameters
                                param_values[param_name] = st.text_input(
                                    f"{param_name} ({data_type})",
                                    key=f"param_{param_name}_{position}"
                                )
                    
                    execute_button = st.form_submit_button("🚀 Execute Function")
                    
                    if execute_button:
                        try:
                            # Build function call
                            if param_values:
                                param_list = [f"'{value}'" if value else 'NULL' for value in param_values.values()]
                                param_string = ', '.join(param_list)
                            else:
                                param_string = ''
                            
                            if routine_type == 'FUNCTION':
                                execute_query = f'SELECT "{schema}"."{routine_name}"({param_string})'
                            else:  # PROCEDURE
                                execute_query = f'CALL "{schema}"."{routine_name}"({param_string})'
                            
                            st.code(execute_query, language='sql')
                            
                            # Execute function
                            result = db_conn.execute_query(execute_query)
                            
                            if result is not None and not result.empty:
                                st.success("✅ Function executed successfully!")
                                st.subheader("📊 Result")
                                st.dataframe(result, use_container_width=True)
                            else:
                                st.success("✅ Function executed successfully!")
                                st.info("Function executed with no return value")
                        
                        except Exception as e:
                            st.error(f"❌ Error executing function: {str(e)}")
        else:
            st.info("No functions or procedures available for execution")
    
    except Exception as e:
        st.error(f"Error loading function executor: {str(e)}")
