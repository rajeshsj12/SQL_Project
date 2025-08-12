import streamlit as st
import pandas as pd
from database.queries import DCL_QUERIES

def show():
    """Display the enhanced DCL operations page"""
    st.header("🔐 DCL Operations (Data Control Language)")
    
    if not st.session_state.get('connected'):
        st.error("Please connect to a database first")
        return
    
    db_conn = st.session_state.db_connection
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Users & Roles", 
        "🔑 Grant Privileges", 
        "🚫 Revoke Privileges", 
        "📊 View Privileges", 
        "🛡️ Security Overview"
    ])
    
    with tab1:
        show_users_and_roles(db_conn)
    
    with tab2:
        show_grant_privileges_enhanced(db_conn)
    
    with tab3:
        show_revoke_privileges_enhanced(db_conn)
    
    with tab4:
        show_view_privileges(db_conn)
    
    with tab5:
        show_security_overview(db_conn)

def show_users_and_roles(db_conn):
    """Display users and roles management"""
    st.subheader("👥 Users & Roles Management")
    
    try:
        # Get all users and roles
        users_df = db_conn.execute_query(DCL_QUERIES['all_users'])
        
        if not users_df.empty:
            # Search functionality
            search_term = st.text_input("🔍 Search users/roles", placeholder="Enter username or role name...")
            
            if search_term:
                filtered_df = users_df[
                    users_df['username'].str.contains(search_term, case=False, na=False)
                ]
            else:
                filtered_df = users_df
            
            # Display users table
            st.dataframe(
                filtered_df,
                column_config={
                    'username': 'Username',
                    'is_superuser': st.column_config.CheckboxColumn('Superuser'),
                    'can_create_role': st.column_config.CheckboxColumn('Create Role'),
                    'can_create_db': st.column_config.CheckboxColumn('Create DB'),
                    'can_login': st.column_config.CheckboxColumn('Can Login'),
                    'can_replicate': st.column_config.CheckboxColumn('Replication'),
                    'valid_until': 'Valid Until'
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Users", len(filtered_df))
            
            with col2:
                superusers = filtered_df['is_superuser'].sum()
                st.metric("Superusers", superusers)
            
            with col3:
                login_users = filtered_df['can_login'].sum()
                st.metric("Login Enabled", login_users)
            
            with col4:
                db_creators = filtered_df['can_create_db'].sum()
                st.metric("DB Creators", db_creators)
        else:
            st.info("No users found")
    
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")

def show_grant_privileges_enhanced(db_conn):
    """Display enhanced grant privileges interface with SQL code generation"""
    st.subheader("🔑 Grant Privileges")
    
    try:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Create new user form
            with st.expander("👤 Create New User/Role", expanded=True):
                with st.form("create_user_form"):
                    username = st.text_input("Username/Role Name", placeholder="Enter username")
                    password = st.text_input("Password (optional for roles)", type="password", placeholder="Enter password")
                    
                    st.write("**Role Attributes:**")
                    col1_form, col2_form = st.columns(2)
                    
                    with col1_form:
                        can_login = st.checkbox("LOGIN", value=True, help="Can connect to database")
                        is_superuser = st.checkbox("SUPERUSER", value=False, help="Has all privileges")
                        can_create_db = st.checkbox("CREATEDB", value=False, help="Can create databases")
                    
                    with col2_form:
                        can_create_role = st.checkbox("CREATEROLE", value=False, help="Can create roles")
                        can_replicate = st.checkbox("REPLICATION", value=False, help="Can replicate")
                        inherit_privileges = st.checkbox("INHERIT", value=True, help="Inherits role privileges")
                    
                    valid_until = st.date_input("Valid Until (optional)", value=None)
                    
                    # Generate SQL preview in real-time
                    if username:
                        role_options = []
                        if can_login:
                            role_options.append("LOGIN")
                        else:
                            role_options.append("NOLOGIN")
                        if is_superuser:
                            role_options.append("SUPERUSER")
                        if can_create_db:
                            role_options.append("CREATEDB")
                        if can_create_role:
                            role_options.append("CREATEROLE")
                        if can_replicate:
                            role_options.append("REPLICATION")
                        if inherit_privileges:
                            role_options.append("INHERIT")
                        else:
                            role_options.append("NOINHERIT")
                        
                        options_str = " ".join(role_options)
                        
                        preview_query = f"CREATE ROLE {username} WITH {options_str}"
                        if password:
                            preview_query += f" PASSWORD '***'"
                        if valid_until:
                            preview_query += f" VALID UNTIL '{valid_until}'"
                        preview_query += ";"
                        
                        st.write("**Generated SQL:**")
                        st.code(preview_query, language='sql')
                    
                    create_user_button = st.form_submit_button("👤 Create User/Role", use_container_width=True)
                    
                    if create_user_button and username:
                        try:
                            # Build CREATE ROLE statement
                            role_options = []
                            if can_login:
                                role_options.append("LOGIN")
                            else:
                                role_options.append("NOLOGIN")
                            if is_superuser:
                                role_options.append("SUPERUSER")
                            if can_create_db:
                                role_options.append("CREATEDB")
                            if can_create_role:
                                role_options.append("CREATEROLE")
                            if can_replicate:
                                role_options.append("REPLICATION")
                            if inherit_privileges:
                                role_options.append("INHERIT")
                            else:
                                role_options.append("NOINHERIT")
                            
                            options_str = " ".join(role_options)
                            
                            query = f"CREATE ROLE {username} WITH {options_str}"
                            if password:
                                query += f" PASSWORD '{password}'"
                            if valid_until:
                                query += f" VALID UNTIL '{valid_until}'"
                            
                            db_conn.execute_query(query, fetch=False)
                            st.success(f"✅ User/Role '{username}' created successfully!")
                            
                            # Show executed SQL
                            with st.expander("📝 Executed SQL"):
                                display_query = query.replace(f"PASSWORD '{password}'", "PASSWORD '***'") if password else query
                                st.code(display_query, language='sql')
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error creating user/role: {str(e)}")
        
        with col2:
            # Grant privileges form
            with st.expander("🔑 Grant Privileges", expanded=True):
                # Get list of users
                users_df = db_conn.execute_query(DCL_QUERIES['all_users'])
                
                if not users_df.empty:
                    user_options = users_df['username'].tolist()
                    
                    with st.form("grant_privileges_form"):
                        selected_user = st.selectbox("Select User/Role", user_options)
                        privilege_type = st.selectbox("Object Type", [
                            "Database", "Schema", "Table", "Sequence", "Function", "Type"
                        ])
                        
                        # Define all available privileges for each type
                        all_privileges = {
                            "Database": ["CONNECT", "CREATE", "TEMPORARY"],
                            "Schema": ["CREATE", "USAGE"],
                            "Table": ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"],
                            "Sequence": ["SELECT", "UPDATE", "USAGE"],
                            "Function": ["EXECUTE"],
                            "Type": ["USAGE"]
                        }
                        
                        # Object selection
                        if privilege_type == "Database":
                            databases = db_conn.get_databases()
                            selected_object = st.selectbox("Select Database", databases)
                        elif privilege_type == "Schema":
                            # Get schemas
                            try:
                                schema_df = db_conn.execute_query("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast') ORDER BY schema_name")
                                if not schema_df.empty:
                                    schema_options = schema_df['schema_name'].tolist()
                                    selected_object = st.selectbox("Select Schema", schema_options)
                                else:
                                    selected_object = st.text_input("Schema Name", value="public")
                            except:
                                selected_object = st.text_input("Schema Name", value="public")
                        elif privilege_type == "Table":
                            # Get tables
                            try:
                                tables_df = db_conn.execute_query("SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('information_schema', 'pg_catalog') ORDER BY schemaname, tablename")
                                if not tables_df.empty:
                                    table_options = [f"{row['schemaname']}.{row['tablename']}" for _, row in tables_df.iterrows()]
                                    selected_object = st.selectbox("Select Table", table_options)
                                else:
                                    selected_object = st.text_input("Table Name", placeholder="schema.table")
                            except:
                                selected_object = st.text_input("Table Name", placeholder="schema.table")
                        elif privilege_type == "Sequence":
                            selected_object = st.text_input("Sequence Name", placeholder="schema.sequence")
                        elif privilege_type == "Function":
                            selected_object = st.text_input("Function Name", placeholder="schema.function()")
                        elif privilege_type == "Type":
                            selected_object = st.text_input("Type Name", placeholder="schema.type")
                        
                        # Checkbox interface for privileges
                        st.write("**Select Privileges:**")
                        
                        # Special "ALL" option
                        grant_all = st.checkbox("ALL PRIVILEGES", key=f"all_{privilege_type}")
                        
                        privileges = []
                        if not grant_all:
                            # Individual privilege checkboxes
                            available_privs = all_privileges.get(privilege_type, [])
                            
                            # Create responsive columns
                            num_cols = min(3, len(available_privs))
                            if num_cols > 0:
                                cols = st.columns(num_cols)
                                for i, priv in enumerate(available_privs):
                                    with cols[i % num_cols]:
                                        if st.checkbox(priv, key=f"priv_{priv}_{privilege_type}"):
                                            privileges.append(priv)
                        else:
                            privileges = ["ALL"]
                        
                        # Optional: Grant option
                        with_grant_option = st.checkbox("WITH GRANT OPTION", help="Allow user to grant these privileges to others")
                        
                        # Generate SQL preview
                        if selected_user and selected_object and (privileges or grant_all):
                            privileges_str = "ALL" if grant_all else ", ".join(privileges)
                            
                            if privilege_type == "Database":
                                preview_query = f"GRANT {privileges_str} ON DATABASE {selected_object} TO {selected_user}"
                            elif privilege_type == "Schema":
                                preview_query = f"GRANT {privileges_str} ON SCHEMA {selected_object} TO {selected_user}"
                            elif privilege_type == "Table":
                                preview_query = f"GRANT {privileges_str} ON TABLE {selected_object} TO {selected_user}"
                            elif privilege_type == "Sequence":
                                preview_query = f"GRANT {privileges_str} ON SEQUENCE {selected_object} TO {selected_user}"
                            elif privilege_type == "Function":
                                preview_query = f"GRANT {privileges_str} ON FUNCTION {selected_object} TO {selected_user}"
                            elif privilege_type == "Type":
                                preview_query = f"GRANT {privileges_str} ON TYPE {selected_object} TO {selected_user}"
                            
                            if with_grant_option:
                                preview_query += " WITH GRANT OPTION"
                            preview_query += ";"
                            
                            st.write("**Generated SQL:**")
                            st.code(preview_query, language='sql')
                        
                        grant_button = st.form_submit_button("🔑 Grant Privileges", use_container_width=True)
                        
                        if grant_button and selected_user and selected_object and (privileges or grant_all):
                            try:
                                privileges_str = "ALL" if grant_all else ", ".join(privileges)
                                
                                if privilege_type == "Database":
                                    query = f"GRANT {privileges_str} ON DATABASE {selected_object} TO {selected_user}"
                                elif privilege_type == "Schema":
                                    query = f"GRANT {privileges_str} ON SCHEMA {selected_object} TO {selected_user}"
                                elif privilege_type == "Table":
                                    query = f"GRANT {privileges_str} ON TABLE {selected_object} TO {selected_user}"
                                elif privilege_type == "Sequence":
                                    query = f"GRANT {privileges_str} ON SEQUENCE {selected_object} TO {selected_user}"
                                elif privilege_type == "Function":
                                    query = f"GRANT {privileges_str} ON FUNCTION {selected_object} TO {selected_user}"
                                elif privilege_type == "Type":
                                    query = f"GRANT {privileges_str} ON TYPE {selected_object} TO {selected_user}"
                                
                                if with_grant_option:
                                    query += " WITH GRANT OPTION"
                                
                                db_conn.execute_query(query, fetch=False)
                                st.success(f"✅ Privileges granted to '{selected_user}' successfully!")
                                
                                # Show executed SQL
                                with st.expander("📝 Executed SQL"):
                                    st.code(query, language='sql')
                                
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error granting privileges: {str(e)}")
                else:
                    st.info("No users available")
    
    except Exception as e:
        st.error(f"Error loading grant privileges: {str(e)}")

def show_revoke_privileges_enhanced(db_conn):
    """Display enhanced revoke privileges interface"""
    st.subheader("🚫 Revoke Privileges")
    
    try:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Drop user/role form
            with st.expander("🗑️ Drop User/Role", expanded=True):
                with st.form("drop_user_form"):
                    # Get list of users
                    users_df = db_conn.execute_query(DCL_QUERIES['all_users'])
                    
                    if not users_df.empty:
                        user_options = users_df['username'].tolist()
                        selected_user = st.selectbox("Select User/Role to Drop", user_options)
                        
                        # Options
                        cascade = st.checkbox("CASCADE", help="Drop objects owned by the role")
                        
                        # Generate SQL preview
                        if selected_user:
                            preview_query = f"DROP ROLE {selected_user}"
                            if cascade:
                                preview_query += " CASCADE"
                            preview_query += ";"
                            
                            st.write("**Generated SQL:**")
                            st.code(preview_query, language='sql')
                        
                        drop_button = st.form_submit_button("🗑️ Drop User/Role", use_container_width=True, type="secondary")
                        
                        if drop_button and selected_user:
                            # Confirmation
                            if st.checkbox(f"I confirm dropping {selected_user}", key="confirm_drop"):
                                try:
                                    query = f"DROP ROLE {selected_user}"
                                    if cascade:
                                        query += " CASCADE"
                                    
                                    db_conn.execute_query(query, fetch=False)
                                    st.success(f"✅ User/Role '{selected_user}' dropped successfully!")
                                    
                                    # Show executed SQL
                                    with st.expander("📝 Executed SQL"):
                                        st.code(query, language='sql')
                                    
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"❌ Error dropping user/role: {str(e)}")
                            else:
                                st.warning("Please confirm the action to proceed")
                    else:
                        st.info("No users available")
        
        with col2:
            # Revoke privileges form
            with st.expander("🚫 Revoke Privileges", expanded=True):
                # Get list of users
                users_df = db_conn.execute_query(DCL_QUERIES['all_users'])
                
                if not users_df.empty:
                    user_options = users_df['username'].tolist()
                    
                    with st.form("revoke_privileges_form"):
                        selected_user = st.selectbox("Select User/Role", user_options, key="revoke_user")
                        privilege_type = st.selectbox("Object Type", [
                            "Database", "Schema", "Table", "Sequence", "Function", "Type"
                        ], key="revoke_type")
                        
                        # Define all available privileges for each type
                        all_privileges = {
                            "Database": ["CONNECT", "CREATE", "TEMPORARY"],
                            "Schema": ["CREATE", "USAGE"],
                            "Table": ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"],
                            "Sequence": ["SELECT", "UPDATE", "USAGE"],
                            "Function": ["EXECUTE"],
                            "Type": ["USAGE"]
                        }
                        
                        # Object selection
                        if privilege_type == "Database":
                            databases = db_conn.get_databases()
                            selected_object = st.selectbox("Select Database", databases, key="revoke_db")
                        elif privilege_type == "Schema":
                            try:
                                schema_df = db_conn.execute_query("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast') ORDER BY schema_name")
                                if not schema_df.empty:
                                    schema_options = schema_df['schema_name'].tolist()
                                    selected_object = st.selectbox("Select Schema", schema_options, key="revoke_schema")
                                else:
                                    selected_object = st.text_input("Schema Name", value="public", key="revoke_schema_text")
                            except:
                                selected_object = st.text_input("Schema Name", value="public", key="revoke_schema_text")
                        elif privilege_type == "Table":
                            try:
                                tables_df = db_conn.execute_query("SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('information_schema', 'pg_catalog') ORDER BY schemaname, tablename")
                                if not tables_df.empty:
                                    table_options = [f"{row['schemaname']}.{row['tablename']}" for _, row in tables_df.iterrows()]
                                    selected_object = st.selectbox("Select Table", table_options, key="revoke_table")
                                else:
                                    selected_object = st.text_input("Table Name", placeholder="schema.table", key="revoke_table_text")
                            except:
                                selected_object = st.text_input("Table Name", placeholder="schema.table", key="revoke_table_text")
                        elif privilege_type == "Sequence":
                            selected_object = st.text_input("Sequence Name", placeholder="schema.sequence", key="revoke_sequence")
                        elif privilege_type == "Function":
                            selected_object = st.text_input("Function Name", placeholder="schema.function()", key="revoke_function")
                        elif privilege_type == "Type":
                            selected_object = st.text_input("Type Name", placeholder="schema.type", key="revoke_type_name")
                        
                        # Checkbox interface for privileges
                        st.write("**Select Privileges to Revoke:**")
                        
                        # Special "ALL" option
                        revoke_all = st.checkbox("ALL PRIVILEGES", key=f"revoke_all_{privilege_type}")
                        
                        privileges = []
                        if not revoke_all:
                            # Individual privilege checkboxes
                            available_privs = all_privileges.get(privilege_type, [])
                            
                            # Create responsive columns
                            num_cols = min(3, len(available_privs))
                            if num_cols > 0:
                                cols = st.columns(num_cols)
                                for i, priv in enumerate(available_privs):
                                    with cols[i % num_cols]:
                                        if st.checkbox(priv, key=f"revoke_priv_{priv}_{privilege_type}"):
                                            privileges.append(priv)
                        else:
                            privileges = ["ALL"]
                        
                        # Options
                        cascade_revoke = st.checkbox("CASCADE", help="Revoke from dependent objects")
                        restrict_revoke = st.checkbox("RESTRICT", help="Fail if dependent objects exist")
                        
                        # Generate SQL preview
                        if selected_user and selected_object and (privileges or revoke_all):
                            privileges_str = "ALL" if revoke_all else ", ".join(privileges)
                            
                            if privilege_type == "Database":
                                preview_query = f"REVOKE {privileges_str} ON DATABASE {selected_object} FROM {selected_user}"
                            elif privilege_type == "Schema":
                                preview_query = f"REVOKE {privileges_str} ON SCHEMA {selected_object} FROM {selected_user}"
                            elif privilege_type == "Table":
                                preview_query = f"REVOKE {privileges_str} ON TABLE {selected_object} FROM {selected_user}"
                            elif privilege_type == "Sequence":
                                preview_query = f"REVOKE {privileges_str} ON SEQUENCE {selected_object} FROM {selected_user}"
                            elif privilege_type == "Function":
                                preview_query = f"REVOKE {privileges_str} ON FUNCTION {selected_object} FROM {selected_user}"
                            elif privilege_type == "Type":
                                preview_query = f"REVOKE {privileges_str} ON TYPE {selected_object} FROM {selected_user}"
                            
                            if cascade_revoke:
                                preview_query += " CASCADE"
                            elif restrict_revoke:
                                preview_query += " RESTRICT"
                            preview_query += ";"
                            
                            st.write("**Generated SQL:**")
                            st.code(preview_query, language='sql')
                        
                        revoke_button = st.form_submit_button("🚫 Revoke Privileges", use_container_width=True, type="secondary")
                        
                        if revoke_button and selected_user and selected_object and (privileges or revoke_all):
                            try:
                                privileges_str = "ALL" if revoke_all else ", ".join(privileges)
                                
                                if privilege_type == "Database":
                                    query = f"REVOKE {privileges_str} ON DATABASE {selected_object} FROM {selected_user}"
                                elif privilege_type == "Schema":
                                    query = f"REVOKE {privileges_str} ON SCHEMA {selected_object} FROM {selected_user}"
                                elif privilege_type == "Table":
                                    query = f"REVOKE {privileges_str} ON TABLE {selected_object} FROM {selected_user}"
                                elif privilege_type == "Sequence":
                                    query = f"REVOKE {privileges_str} ON SEQUENCE {selected_object} FROM {selected_user}"
                                elif privilege_type == "Function":
                                    query = f"REVOKE {privileges_str} ON FUNCTION {selected_object} FROM {selected_user}"
                                elif privilege_type == "Type":
                                    query = f"REVOKE {privileges_str} ON TYPE {selected_object} FROM {selected_user}"
                                
                                if cascade_revoke:
                                    query += " CASCADE"
                                elif restrict_revoke:
                                    query += " RESTRICT"
                                
                                db_conn.execute_query(query, fetch=False)
                                st.success(f"✅ Privileges revoked from '{selected_user}' successfully!")
                                
                                # Show executed SQL
                                with st.expander("📝 Executed SQL"):
                                    st.code(query, language='sql')
                                
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error revoking privileges: {str(e)}")
                else:
                    st.info("No users available")
    
    except Exception as e:
        st.error(f"Error loading revoke privileges: {str(e)}")

def show_view_privileges(db_conn):
    """Display current privileges for users"""
    st.subheader("📊 View Current Privileges")
    
    try:
        # Get user privileges query
        privileges_query = """
        SELECT 
            grantee as username,
            table_catalog as database_name,
            table_schema as schema_name,
            table_name,
            privilege_type,
            is_grantable
        FROM information_schema.table_privileges
        WHERE grantee NOT IN ('PUBLIC', 'postgres')
        ORDER BY grantee, table_schema, table_name, privilege_type
        """
        
        privileges_df = db_conn.execute_query(privileges_query)
        
        if not privileges_df.empty:
            # User selection for filtering
            users = privileges_df['username'].unique()
            selected_user = st.selectbox("Select User to View Privileges", ['All Users'] + list(users))
            
            if selected_user != 'All Users':
                filtered_df = privileges_df[privileges_df['username'] == selected_user]
            else:
                filtered_df = privileges_df
            
            # Display privileges
            st.dataframe(
                filtered_df,
                column_config={
                    'username': 'User',
                    'database_name': 'Database',
                    'schema_name': 'Schema',
                    'table_name': 'Table',
                    'privilege_type': 'Privilege',
                    'is_grantable': st.column_config.CheckboxColumn('Grantable')
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Summary by user
            if selected_user != 'All Users':
                st.subheader(f"Privilege Summary for {selected_user}")
                privilege_summary = filtered_df['privilege_type'].value_counts()
                
                col1, col2 = st.columns(2)
                with col1:
                    for privilege, count in privilege_summary.items():
                        st.metric(privilege, count)
            
        else:
            st.info("No table privileges found")
        
        # Also show database privileges
        st.subheader("Database Privileges")
        
        db_privileges_query = """
        SELECT 
            datname as database_name,
            usename as username,
            'CONNECT' as privilege_type
        FROM pg_database d
        JOIN pg_user u ON has_database_privilege(u.usename, d.datname, 'CONNECT')
        WHERE d.datistemplate = false
        ORDER BY datname, usename
        """
        
        try:
            db_privileges_df = db_conn.execute_query(db_privileges_query)
            if not db_privileges_df.empty:
                st.dataframe(
                    db_privileges_df,
                    column_config={
                        'database_name': 'Database',
                        'username': 'User',
                        'privilege_type': 'Privilege'
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No database privileges found")
        except:
            st.info("Unable to retrieve database privileges")
    
    except Exception as e:
        st.error(f"Error loading privileges: {str(e)}")

def show_security_overview(db_conn):
    """Display security overview and recommendations"""
    st.subheader("🛡️ Security Overview")
    
    try:
        # Security metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Get security-related statistics
        users_df = db_conn.execute_query(DCL_QUERIES['all_users'])
        
        if not users_df.empty:
            with col1:
                total_users = len(users_df)
                st.metric("Total Users", total_users)
            
            with col2:
                superusers = users_df['is_superuser'].sum()
                st.metric("Superusers", superusers, delta=f"{(superusers/total_users*100):.1f}% of total")
            
            with col3:
                login_users = users_df['can_login'].sum()
                st.metric("Login Enabled", login_users)
            
            with col4:
                no_password_users = users_df[users_df['password'].isna()].shape[0] if 'password' in users_df.columns else 0
                st.metric("No Password", no_password_users)
        
        # Security recommendations
        st.subheader("🔒 Security Recommendations")
        
        recommendations = []
        
        if not users_df.empty:
            # Check for too many superusers
            superuser_count = users_df['is_superuser'].sum()
            if superuser_count > 2:
                recommendations.append({
                    "level": "warning",
                    "title": "Too Many Superusers",
                    "description": f"You have {superuser_count} superusers. Consider reducing this number for better security.",
                    "action": "Review and remove unnecessary superuser privileges"
                })
            
            # Check for users without passwords
            if 'password' in users_df.columns:
                no_password = users_df[users_df['password'].isna()].shape[0]
                if no_password > 0:
                    recommendations.append({
                        "level": "error",
                        "title": "Users Without Passwords",
                        "description": f"{no_password} users don't have passwords set.",
                        "action": "Set passwords for all user accounts"
                    })
            
            # Check for default/weak usernames
            common_usernames = ['admin', 'root', 'user', 'test', 'guest']
            weak_users = users_df[users_df['username'].isin(common_usernames)]
            if not weak_users.empty:
                recommendations.append({
                    "level": "warning",
                    "title": "Common Usernames Detected",
                    "description": f"Found common usernames: {', '.join(weak_users['username'].tolist())}",
                    "action": "Consider renaming accounts with more specific names"
                })
        
        # Display recommendations
        if recommendations:
            for rec in recommendations:
                if rec["level"] == "error":
                    st.error(f"🚨 **{rec['title']}**: {rec['description']}")
                    st.write(f"**Action:** {rec['action']}")
                elif rec["level"] == "warning":
                    st.warning(f"⚠️ **{rec['title']}**: {rec['description']}")
                    st.write(f"**Action:** {rec['action']}")
                st.write("---")
        else:
            st.success("✅ No major security issues detected")
        
        # Security best practices
        with st.expander("📚 Security Best Practices"):
            st.markdown("""
            ### PostgreSQL Security Best Practices
            
            1. **Principle of Least Privilege**
               - Grant only the minimum privileges necessary
               - Regularly audit and review user permissions
            
            2. **Strong Authentication**
               - Use strong, unique passwords
               - Consider certificate-based authentication
               - Enable password encryption
            
            3. **Role Management**
               - Use roles instead of individual user grants
               - Create functional roles (e.g., readonly, admin)
               - Avoid excessive superuser privileges
            
            4. **Network Security**
               - Configure pg_hba.conf properly
               - Use SSL/TLS connections
               - Restrict network access
            
            5. **Monitoring**
               - Enable logging of connections and statements
               - Monitor failed login attempts
               - Regular security audits
            
            6. **Regular Maintenance**
               - Remove unused accounts
               - Update passwords regularly
               - Keep PostgreSQL updated
            """)
    
    except Exception as e:
        st.error(f"Error loading security overview: {str(e)}")