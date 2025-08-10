"""
SQL queries for database operations
"""

# Dashboard queries
DASHBOARD_QUERIES = {
    'table_count': """
        SELECT COUNT(*) as count
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
    """,
    
    'view_count': """
        SELECT COUNT(*) as count
        FROM information_schema.views 
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
    """,
    
    'function_count': """
        SELECT COUNT(*) as count
        FROM information_schema.routines 
        WHERE routine_schema NOT IN ('information_schema', 'pg_catalog')
        AND routine_type = 'FUNCTION'
    """,
    
    'procedure_count': """
        SELECT COUNT(*) as count
        FROM information_schema.routines 
        WHERE routine_schema NOT IN ('information_schema', 'pg_catalog')
        AND routine_type = 'PROCEDURE'
    """,
    
    'trigger_count': """
        SELECT COUNT(*) as count
        FROM information_schema.triggers
        WHERE trigger_schema NOT IN ('information_schema', 'pg_catalog')
    """,
    
    'index_count': """
        SELECT COUNT(*) as count
        FROM pg_indexes 
        WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
    """,
    
    'sequence_count': """
        SELECT COUNT(*) as count
        FROM information_schema.sequences
        WHERE sequence_schema NOT IN ('information_schema', 'pg_catalog')
    """
}

# Table queries
TABLE_QUERIES = {
    'all_tables': """
        SELECT 
            t.table_schema,
            t.table_name,
            t.table_type,
            COALESCE(
                (SELECT COUNT(*) 
                 FROM information_schema.columns c 
                 WHERE c.table_schema = t.table_schema 
                 AND c.table_name = t.table_name), 0
            ) as column_count,
            pg_size_pretty(pg_total_relation_size(quote_ident(t.table_schema)||'.'||quote_ident(t.table_name))) as size
        FROM information_schema.tables t
        WHERE t.table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY t.table_schema, t.table_name
    """,
    
    'table_columns': """
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default,
            ordinal_position
        FROM information_schema.columns 
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
    """,
    
    'table_indexes': """
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes 
        WHERE schemaname = %s AND tablename = %s
    """,
    
    'table_constraints': """
        SELECT 
            constraint_name,
            constraint_type
        FROM information_schema.table_constraints 
        WHERE table_schema = %s AND table_name = %s
    """
}

# Function queries
FUNCTION_QUERIES = {
    'all_functions': """
        SELECT 
            r.routine_schema,
            r.routine_name,
            r.routine_type,
            r.data_type as return_type,
            r.routine_definition,
            p.prosrc as source_code
        FROM information_schema.routines r
        LEFT JOIN pg_proc p ON r.routine_name = p.proname
        WHERE r.routine_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY r.routine_schema, r.routine_name
    """,
    
    'function_parameters': """
        SELECT 
            parameter_name,
            data_type,
            parameter_mode,
            ordinal_position
        FROM information_schema.parameters 
        WHERE specific_schema = %s AND specific_name = %s
        ORDER BY ordinal_position
    """
}

# Trigger queries
TRIGGER_QUERIES = {
    'all_triggers': """
        SELECT 
            t.trigger_schema,
            t.trigger_name,
            t.event_manipulation,
            t.event_object_table,
            t.action_timing,
            t.action_statement,
            t.action_orientation
        FROM information_schema.triggers t
        WHERE t.trigger_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY t.trigger_schema, t.trigger_name
    """,
    
    'event_triggers': """
        SELECT 
            evtname as trigger_name,
            evtevent as event,
            evtowner::regrole as owner,
            evtenabled as enabled,
            evttags as tags
        FROM pg_event_trigger
        ORDER BY evtname
    """
}

# DCL queries
DCL_QUERIES = {
    'all_users': """
        SELECT 
            rolname as username,
            rolsuper as is_superuser,
            rolcreaterole as can_create_role,
            rolcreatedb as can_create_db,
            rolcanlogin as can_login,
            rolreplication as can_replicate,
            rolvaliduntil as valid_until
        FROM pg_roles
        ORDER BY rolname
    """,
    
    'user_privileges': """
        SELECT 
            grantee,
            table_schema,
            table_name,
            privilege_type,
            is_grantable
        FROM information_schema.table_privileges
        WHERE grantee = %s
        ORDER BY table_schema, table_name, privilege_type
    """,
    
    'schema_privileges': """
        SELECT 
            grantee,
            schema_name,
            privilege_type,
            is_grantable
        FROM information_schema.schema_privileges
        WHERE grantee = %s
        ORDER BY schema_name, privilege_type
    """,
    
    'database_privileges': """
        SELECT 
            d.datname as database_name,
            r.rolname as username,
            has_database_privilege(r.rolname, d.datname, 'CONNECT') as connect,
            has_database_privilege(r.rolname, d.datname, 'CREATE') as create,
            has_database_privilege(r.rolname, d.datname, 'TEMP') as temp
        FROM pg_database d
        CROSS JOIN pg_roles r
        WHERE d.datistemplate = false
        AND r.rolcanlogin = true
        ORDER BY d.datname, r.rolname
    """
}

# Monitoring queries
MONITORING_QUERIES = {
    'active_queries': """
        SELECT 
            pid,
            usename,
            application_name,
            client_addr,
            state,
            query_start,
            query
        FROM pg_stat_activity 
        WHERE state = 'active'
        AND query NOT LIKE '%pg_stat_activity%'
        ORDER BY query_start DESC
    """,
    
    'database_stats': """
        SELECT 
            datname,
            numbackends as connections,
            xact_commit as commits,
            xact_rollback as rollbacks,
            blks_read as blocks_read,
            blks_hit as blocks_hit,
            tup_returned as tuples_returned,
            tup_fetched as tuples_fetched,
            tup_inserted as tuples_inserted,
            tup_updated as tuples_updated,
            tup_deleted as tuples_deleted
        FROM pg_stat_database 
        WHERE datname = current_database()
    """,
    
    'table_stats': """
        SELECT 
            schemaname,
            tablename,
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
        ORDER BY schemaname, tablename
    """,
    
    'index_usage': """
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched
        FROM pg_stat_user_indexes
        ORDER BY schemaname, tablename, indexname
    """
}
