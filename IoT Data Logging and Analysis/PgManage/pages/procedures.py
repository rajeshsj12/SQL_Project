import streamlit as st
import pandas as pd

def show():
    """Display the procedures page"""
    st.header("🔧 Stored Procedures Management")
    
    if not st.session_state.get('connected'):
        st.error("Please connect to a database first")
        return
    
    db_conn = st.session_state.db_connection
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📊 All Procedures", "🔍 Procedure Details", "▶️ Execute Procedure"])
    
    with tab1:
        show_all_procedures(db_conn)
    
    with tab2:
        show_procedure_details(db_conn)
    
    with tab3:
        show_procedure_executor(db_conn)

def show_all_procedures(db_conn):
    """Display all stored procedures"""
    st.subheader("📊 All Stored Procedures")
    
    try:
        # Get all procedures
        procedures_query = """
        SELECT 
            routine_schema,
            routine_name,
            routine_type,
            created,
            last_altered,
            routine_definition
        FROM information_schema.routines 
        WHERE routine_type = 'PROCEDURE'
        AND routine_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY routine_schema, routine_name
        """
        
        procedures_df = db_conn.execute_query(procedures_query)
        
        if not procedures_df.empty:
            # Search functionality
            search_term = st.text_input("🔍 Search procedures", placeholder="Enter procedure name or schema...")
            
            if search_term:
                filtered_df = procedures_df[
                    procedures_df['routine_name'].str.contains(search_term, case=False, na=False) |
                    procedures_df['routine_schema'].str.contains(search_term, case=False, na=False)
                ]
            else:
                filtered_df = procedures_df
            
            # Display procedures
            st.dataframe(
                filtered_df[['routine_schema', 'routine_name', 'created', 'last_altered']],
                column_config={
                    'routine_schema': 'Schema',
                    'routine_name': 'Procedure Name',
                    'created': 'Created',
                    'last_altered': 'Last Modified'
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Summary statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Procedures", len(filtered_df))
            
            with col2:
                schemas = filtered_df['routine_schema'].nunique()
                st.metric("Schemas", schemas)
        else:
            st.info("No stored procedures found in the current database")
    
    except Exception as e:
        st.error(f"Error loading procedures: {str(e)}")

def show_procedure_details(db_conn):
    """Display detailed information about a specific procedure"""
    st.subheader("🔍 Procedure Details")
    
    try:
        # Get list of procedures for selection
        procedures_query = """
        SELECT 
            routine_schema,
            routine_name,
            routine_definition
        FROM information_schema.routines 
        WHERE routine_type = 'PROCEDURE'
        AND routine_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY routine_schema, routine_name
        """
        
        procedures_df = db_conn.execute_query(procedures_query)
        
        if not procedures_df.empty:
            # Procedure selection
            procedure_options = [f"{row['routine_schema']}.{row['routine_name']}" for _, row in procedures_df.iterrows()]
            
            selected_procedure = st.selectbox("Select a procedure", procedure_options)
            
            if selected_procedure:
                schema, procedure_name = selected_procedure.split('.', 1)
                
                # Get procedure details
                procedure_row = procedures_df[
                    (procedures_df['routine_schema'] == schema) &
                    (procedures_df['routine_name'] == procedure_name)
                ].iloc[0]
                
                # Display procedure information
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Schema:** {procedure_row['routine_schema']}")
                    st.write(f"**Name:** {procedure_row['routine_name']}")
                
                with col2:
                    st.write(f"**Type:** PROCEDURE")
                
                # Show parameters
                st.subheader("📋 Parameters")
                show_procedure_parameters(db_conn, schema, procedure_name)
                
                # Show procedure source code
                st.subheader("📝 Source Code")
                if pd.notna(procedure_row['routine_definition']):
                    st.code(procedure_row['routine_definition'], language='sql')
                else:
                    st.info("Source code not available")
                
                # Show procedure dependencies
                st.subheader("🔗 Dependencies")
                show_procedure_dependencies(db_conn, schema, procedure_name)
        else:
            st.info("No stored procedures available")
    
    except Exception as e:
        st.error(f"Error loading procedure details: {str(e)}")

def show_procedure_parameters(db_conn, schema, procedure_name):
    """Display procedure parameters"""
    try:
        # Get procedure parameters
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
        cursor.execute(params_query, (schema, procedure_name))
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
                    'Mode': 'Mode (IN/OUT/INOUT)',
                    'Position': st.column_config.NumberColumn('Position')
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No parameters found")
    
    except Exception as e:
        st.error(f"Error loading parameters: {str(e)}")

def show_procedure_dependencies(db_conn, schema, procedure_name):
    """Display procedure dependencies"""
    try:
        # Get procedure dependencies
        deps_query = """
        SELECT DISTINCT
            referenced_object_schema,
            referenced_object_name,
            referenced_object_type
        FROM information_schema.routine_privileges rp
        WHERE rp.routine_schema = %s AND rp.routine_name = %s
        """
        
        cursor = db_conn.connection.cursor()
        cursor.execute(deps_query, (schema, procedure_name))
        dependencies = cursor.fetchall()
        cursor.close()
        
        if dependencies:
            deps_df = pd.DataFrame(dependencies, columns=[
                'Referenced Schema', 'Referenced Object', 'Object Type'
            ])
            
            st.dataframe(
                deps_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No dependencies found")
    
    except Exception as e:
        st.info("Dependency information not available")

def show_procedure_executor(db_conn):
    """Display procedure execution interface"""
    st.subheader("▶️ Execute Stored Procedure")
    
    try:
        # Get list of procedures for selection
        procedures_query = """
        SELECT 
            routine_schema,
            routine_name
        FROM information_schema.routines 
        WHERE routine_type = 'PROCEDURE'
        AND routine_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY routine_schema, routine_name
        """
        
        procedures_df = db_conn.execute_query(procedures_query)
        
        if not procedures_df.empty:
            # Procedure selection
            procedure_options = [f"{row['routine_schema']}.{row['routine_name']}" for _, row in procedures_df.iterrows()]
            
            selected_procedure = st.selectbox("Select a procedure to execute", procedure_options, key="exec_procedure_select")
            
            if selected_procedure:
                schema, procedure_name = selected_procedure.split('.', 1)
                
                # Get procedure parameters
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
                cursor.execute(params_query, (schema, procedure_name))
                parameters = cursor.fetchall()
                cursor.close()
                
                # Create input form
                with st.form("procedure_execution_form"):
                    st.write(f"**Executing:** {schema}.{procedure_name}")
                    
                    param_values = {}
                    if parameters:
                        st.write("**Input Parameters:**")
                        for param_name, data_type, param_mode, position in parameters:
                            if param_name:  # Skip unnamed parameters
                                param_values[param_name] = st.text_input(
                                    f"{param_name} ({data_type}) - {param_mode}",
                                    key=f"proc_param_{param_name}_{position}"
                                )
                    
                    execute_button = st.form_submit_button("🚀 Execute Procedure")
                    
                    if execute_button:
                        try:
                            # Build procedure call
                            if param_values:
                                param_list = [f"'{value}'" if value else 'NULL' for value in param_values.values()]
                                param_string = ', '.join(param_list)
                            else:
                                param_string = ''
                            
                            execute_query = f'CALL "{schema}"."{procedure_name}"({param_string})'
                            
                            st.code(execute_query, language='sql')
                            
                            # Execute procedure
                            result = db_conn.execute_query(execute_query, fetch=False)
                            
                            st.success("✅ Procedure executed successfully!")
                            
                            # Check for any result sets (some procedures might return data)
                            try:
                                cursor = db_conn.connection.cursor()
                                if cursor.description:
                                    result_data = cursor.fetchall()
                                    if result_data:
                                        result_df = pd.DataFrame(result_data)
                                        st.subheader("📊 Result")
                                        st.dataframe(result_df, use_container_width=True)
                                cursor.close()
                            except:
                                pass  # No result set to display
                        
                        except Exception as e:
                            st.error(f"❌ Error executing procedure: {str(e)}")
        else:
            st.info("No stored procedures available for execution")
    
    except Exception as e:
        st.error(f"Error loading procedure executor: {str(e)}")
