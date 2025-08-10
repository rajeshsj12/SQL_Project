import streamlit as st
import pandas as pd
from database.queries import DCL_QUERIES

def show():
    """Display the DCL operations page"""
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
        show_grant_privileges(db_conn)
    
    with tab3:
        show_revoke_privileges(db_conn)
    
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
                total_users = len(filtered_df[filtered_df['can_login'] == True])
                st.metric("Login Users", total_users)
            
            with col2:
                superusers = len(filtered_df[filtered_df['is_superuser'] == True])
                st.metric("Superusers", superusers)
            
            with col3:
                role_creators = len(filtered_df[filtered_df['can_create_role'] == True])
                st.metric("Role Creators", role_creators)
            
            with col4:
                db_creators = len(filtered_df[filtered_df['can_create_db'] == True])
                st.metric("DB Creators", db_creators)
            
            # User/Role creation form
            st.subheader("➕ Create New User/Role")
            
            with st.form("create_user_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_username = st.text_input("Username")
                    new_password = st.text_input("Password", type="password")
                    can_login = st.checkbox("Can Login", value=True)
                    is_superuser = st.checkbox("Superuser")
                
                with col2:
                    can_create_role = st.checkbox("Can Create Role")
                    can_create_db = st.checkbox("Can Create Database")
                    can_replicate = st.checkbox("Replication")
                    valid_until = st.date_input("Valid Until (optional)")
                
                create_button = st.form_submit_button("🔐 Create User/Role")
                
                if create_button and new_username:
                    try:
                        # Build CREATE ROLE command
                        role_options = []
                        
                        if can_login:
                            role_options.append("LOGIN")
                        if is_superuser:
                            role_options.append("SUPERUSER")
                        if can_create_role:
                            role_options.append("CREATEROLE")
                        if can_create_db:
                            role_options.append("CREATEDB")
                        if can_replicate:
                            role_options.append("REPLICATION")
                        
                        if new_password:
                            role_options.append(f"PASSWORD '{new_password}'")
                        
                        if valid_until:
                            role_options.append(f"VALID UNTIL '{valid_until}'")
                        
                        options_str = " ".join(role_options)
                        create_query = f'CREATE ROLE "{new_username}" {options_str}'
                        
                        db_conn.execute_query(create_query, fetch=False)
                        st.success(f"✅ User/Role '{new_username}' created successfully!")
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Error creating user/role: {str(e)}")
        else:
            st.info("No users or roles found")
    
    except Exception as e:
        st.error(f"Error loading users and roles: {str(e)}")

def show_grant_privileges(db_conn):
    """Display grant privileges interface"""
    st.subheader("🔑 Grant Privileges")
    
    # Get users list
    try:
        users_df = db_conn.execute_query(DCL_QUERIES['all_users'])
        user_list = users_df['username'].tolist() if not users_df.empty else []
        
        # Get tables list
        tables_query = """
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY table_schema, table_name
        """
        tables_df = db_conn.execute_query(tables_query)
        table_list = [f"{row['table_schema']}.{row['table_name']}" for _, row in tables_df.iterrows()] if not tables_df.empty else []
        
        # Grant privileges form
        with st.form("grant_privileges_form"):
            st.write("**Grant Table Privileges**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_user = st.selectbox("Select User/Role", user_list)
                selected_table = st.selectbox("Select Table", table_list)
            
            with col2:
                privileges = st.multiselect(
                    "Select Privileges",
                    ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"],
                    default=["SELECT"]
                )
                with_grant_option = st.checkbox("WITH GRANT OPTION")
            
            grant_button = st.form_submit_button("🔑 Grant Privileges")
            
            if grant_button and selected_user and selected_table and privileges:
                try:
                    privileges_str = ", ".join(privileges)
                    grant_option = " WITH GRANT OPTION" if with_grant_option else ""
                    
                    grant_query = f'GRANT {privileges_str} ON TABLE "{selected_table}" TO "{selected_user}"{grant_option}'
                    
                    db_conn.execute_query(grant_query, fetch=False)
                    st.success(f"✅ Privileges {privileges_str} granted to {selected_user} on {selected_table}")
                
                except Exception as e:
                    st.error(f"❌ Error granting privileges: {str(e)}")
        
        # Grant schema privileges
        st.write("---")
        
        with st.form("grant_schema_privileges_form"):
            st.write("**Grant Schema Privileges**")
            
            # Get schemas list
            schemas_query = """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
            ORDER BY schema_name
            """
            schemas_df = db_conn.execute_query(schemas_query)
            schema_list = schemas_df['schema_name'].tolist() if not schemas_df.empty else []
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_user_schema = st.selectbox("Select User/Role", user_list, key="schema_user")
                selected_schema = st.selectbox("Select Schema", schema_list)
            
            with col2:
                schema_privileges = st.multiselect(
                    "Select Schema Privileges",
                    ["USAGE", "CREATE"],
                    default=["USAGE"]
                )
            
            grant_schema_button = st.form_submit_button("🔑 Grant Schema Privileges")
            
            if grant_schema_button and selected_user_schema and selected_schema and schema_privileges:
                try:
                    privileges_str = ", ".join(schema_privileges)
                    grant_query = f'GRANT {privileges_str} ON SCHEMA "{selected_schema}" TO "{selected_user_schema}"'
                    
                    db_conn.execute_query(grant_query, fetch=False)
                    st.success(f"✅ Schema privileges {privileges_str} granted to {selected_user_schema} on {selected_schema}")
                
                except Exception as e:
                    st.error(f"❌ Error granting schema privileges: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading grant privileges interface: {str(e)}")

def show_revoke_privileges(db_conn):
    """Display revoke privileges interface"""
    st.subheader("🚫 Revoke Privileges")
    
    try:
        # Get users list
        users_df = db_conn.execute_query(DCL_QUERIES['all_users'])
        user_list = users_df['username'].tolist() if not users_df.empty else []
        
        # Get tables list
        tables_query = """
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY table_schema, table_name
        """
        tables_df = db_conn.execute_query(tables_query)
        table_list = [f"{row['table_schema']}.{row['table_name']}" for _, row in tables_df.iterrows()] if not tables_df.empty else []
        
        # Revoke table privileges form
        with st.form("revoke_privileges_form"):
            st.write("**Revoke Table Privileges**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_user = st.selectbox("Select User/Role", user_list)
                selected_table = st.selectbox("Select Table", table_list)
            
            with col2:
                privileges = st.multiselect(
                    "Select Privileges to Revoke",
                    ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "ALL"],
                    default=["SELECT"]
                )
                cascade_option = st.checkbox("CASCADE (revoke from dependent objects)")
            
            revoke_button = st.form_submit_button("🚫 Revoke Privileges")
            
            if revoke_button and selected_user and selected_table and privileges:
                try:
                    privileges_str = ", ".join(privileges)
                    cascade_str = " CASCADE" if cascade_option else ""
                    
                    revoke_query = f'REVOKE {privileges_str} ON TABLE "{selected_table}" FROM "{selected_user}"{cascade_str}'
                    
                    db_conn.execute_query(revoke_query, fetch=False)
                    st.success(f"✅ Privileges {privileges_str} revoked from {selected_user} on {selected_table}")
                
                except Exception as e:
                    st.error(f"❌ Error revoking privileges: {str(e)}")
        
        # Revoke schema privileges
        st.write("---")
        
        with st.form("revoke_schema_privileges_form"):
            st.write("**Revoke Schema Privileges**")
            
            # Get schemas list
            schemas_query = """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
            ORDER BY schema_name
            """
            schemas_df = db_conn.execute_query(schemas_query)
            schema_list = schemas_df['schema_name'].tolist() if not schemas_df.empty else []
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_user_schema = st.selectbox("Select User/Role", user_list, key="revoke_schema_user")
                selected_schema = st.selectbox("Select Schema", schema_list, key="revoke_schema")
            
            with col2:
                schema_privileges = st.multiselect(
                    "Select Schema Privileges to Revoke",
                    ["USAGE", "CREATE", "ALL"],
                    default=["USAGE"]
                )
            
            revoke_schema_button = st.form_submit_button("🚫 Revoke Schema Privileges")
            
            if revoke_schema_button and selected_user_schema and selected_schema and schema_privileges:
                try:
                    privileges_str = ", ".join(schema_privileges)
                    revoke_query = f'REVOKE {privileges_str} ON SCHEMA "{selected_schema}" FROM "{selected_user_schema}"'
                    
                    db_conn.execute_query(revoke_query, fetch=False)
                    st.success(f"✅ Schema privileges {privileges_str} revoked from {selected_user_schema} on {selected_schema}")
                
                except Exception as e:
                    st.error(f"❌ Error revoking schema privileges: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading revoke privileges interface: {str(e)}")

def show_view_privileges(db_conn):
    """Display current privileges for users"""
    st.subheader("📊 View Privileges")
    
    try:
        # Get users list
        users_df = db_conn.execute_query(DCL_QUERIES['all_users'])
        user_list = ["All Users"] + users_df['username'].tolist() if not users_df.empty else []
        
        # User selection
        selected_user = st.selectbox("Select User/Role to view privileges", user_list)
        
        if selected_user and selected_user != "All Users":
            # Show table privileges
            st.write(f"**Table Privileges for {selected_user}**")
            
            cursor = db_conn.connection.cursor()
            cursor.execute(DCL_QUERIES['user_privileges'], (selected_user,))
            table_privileges = cursor.fetchall()
            cursor.close()
            
            if table_privileges:
                table_priv_df = pd.DataFrame(table_privileges, columns=[
                    'Grantee', 'Schema', 'Table', 'Privilege', 'Grantable'
                ])
                
                st.dataframe(
                    table_priv_df,
                    column_config={
                        'Grantee': 'User',
                        'Schema': 'Schema',
                        'Table': 'Table',
                        'Privilege': 'Privilege Type',
                        'Grantable': st.column_config.CheckboxColumn('Can Grant')
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info(f"No table privileges found for {selected_user}")
            
            # Show schema privileges
            st.write(f"**Schema Privileges for {selected_user}**")
            
            cursor = db_conn.connection.cursor()
            cursor.execute(DCL_QUERIES['schema_privileges'], (selected_user,))
            schema_privileges = cursor.fetchall()
            cursor.close()
            
            if schema_privileges:
                schema_priv_df = pd.DataFrame(schema_privileges, columns=[
                    'Grantee', 'Schema', 'Privilege', 'Grantable'
                ])
                
                st.dataframe(
                    schema_priv_df,
                    column_config={
                        'Grantee': 'User',
                        'Schema': 'Schema',
                        'Privilege': 'Privilege Type',
                        'Grantable': st.column_config.CheckboxColumn('Can Grant')
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info(f"No schema privileges found for {selected_user}")
        
        elif selected_user == "All Users":
            # Show privileges summary for all users
            st.write("**All User Privileges Summary**")
            
            # Table privileges summary
            all_table_privileges_query = """
            SELECT 
                grantee,
                COUNT(*) as total_privileges,
                COUNT(DISTINCT table_schema) as schemas_count,
                COUNT(DISTINCT table_name) as tables_count
            FROM information_schema.table_privileges
            WHERE grantee IN (SELECT rolname FROM pg_roles WHERE rolcanlogin = true)
            GROUP BY grantee
            ORDER BY total_privileges DESC
            """
            
            all_priv_df = db_conn.execute_query(all_table_privileges_query)
            
            if not all_priv_df.empty:
                st.dataframe(
                    all_priv_df,
                    column_config={
                        'grantee': 'User',
                        'total_privileges': st.column_config.NumberColumn('Total Privileges'),
                        'schemas_count': st.column_config.NumberColumn('Schemas'),
                        'tables_count': st.column_config.NumberColumn('Tables')
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No privilege data available")
    
    except Exception as e:
        st.error(f"Error loading privileges view: {str(e)}")

def show_security_overview(db_conn):
    """Display security overview and recommendations"""
    st.subheader("🛡️ Security Overview")
    
    try:
        # Security metrics
        col1, col2, col3 = st.columns(3)
        
        # Get security-related metrics
        users_df = db_conn.execute_query(DCL_QUERIES['all_users'])
        
        with col1:
            superuser_count = len(users_df[users_df['is_superuser'] == True]) if not users_df.empty else 0
            st.metric("🔴 Superusers", superuser_count)
            
            if superuser_count > 2:
                st.warning("⚠️ Too many superusers detected")
        
        with col2:
            login_users = len(users_df[users_df['can_login'] == True]) if not users_df.empty else 0
            st.metric("👤 Login Users", login_users)
        
        with col3:
            role_creators = len(users_df[users_df['can_create_role'] == True]) if not users_df.empty else 0
            st.metric("🔧 Role Creators", role_creators)
        
        # Security checks
        st.subheader("🔍 Security Checks")
        
        security_checks = []
        
        # Check for users without passwords
        no_password_query = """
        SELECT rolname 
        FROM pg_roles 
        WHERE rolcanlogin = true 
        AND rolpassword IS NULL
        """
        no_password_users = db_conn.execute_query(no_password_query)
        
        if not no_password_users.empty:
            security_checks.append({
                'status': '🔴 CRITICAL',
                'issue': 'Users without passwords',
                'count': len(no_password_users),
                'description': 'Login users without passwords pose security risk'
            })
        
        # Check for expired accounts
        expired_query = """
        SELECT rolname 
        FROM pg_roles 
        WHERE rolcanlogin = true 
        AND rolvaliduntil < NOW()
        """
        expired_users = db_conn.execute_query(expired_query)
        
        if not expired_users.empty:
            security_checks.append({
                'status': '🟡 WARNING',
                'issue': 'Expired user accounts',
                'count': len(expired_users),
                'description': 'User accounts that have expired but are still active'
            })
        
        # Check for excessive superusers
        if superuser_count > 2:
            security_checks.append({
                'status': '🟡 WARNING',
                'issue': 'Too many superusers',
                'count': superuser_count,
                'description': 'Consider reducing the number of superuser accounts'
            })
        
        # Display security checks
        if security_checks:
            for check in security_checks:
                st.error(f"{check['status']} {check['issue']}: {check['count']} found")
                st.write(f"   └─ {check['description']}")
        else:
            st.success("✅ No major security issues detected")
        
        # Database connections overview
        st.subheader("🔗 Database Connections")
        
        db_privileges = db_conn.execute_query(DCL_QUERIES['database_privileges'])
        
        if not db_privileges.empty:
            # Filter for current database
            current_db = st.session_state.current_database
            current_db_privs = db_privileges[db_privileges['database_name'] == current_db]
            
            if not current_db_privs.empty:
                st.dataframe(
                    current_db_privs,
                    column_config={
                        'database_name': 'Database',
                        'username': 'User',
                        'connect': st.column_config.CheckboxColumn('Connect'),
                        'create': st.column_config.CheckboxColumn('Create'),
                        'temp': st.column_config.CheckboxColumn('Temp')
                    },
                    use_container_width=True,
                    hide_index=True
                )
        
        # Security recommendations
        st.subheader("💡 Security Recommendations")
        
        recommendations = [
            "🔐 Use strong passwords for all user accounts",
            "🚫 Limit superuser privileges to essential accounts only",
            "🔄 Regularly review and audit user privileges",
            "⏰ Set expiration dates for temporary accounts",
            "📊 Monitor database access logs regularly",
            "🛡️ Use SSL/TLS connections in production",
            "🔒 Implement principle of least privilege",
            "📝 Document all privilege grants and their purposes"
        ]
        
        for rec in recommendations:
            st.write(f"• {rec}")
    
    except Exception as e:
        st.error(f"Error loading security overview: {str(e)}")
