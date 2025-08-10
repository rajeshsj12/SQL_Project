import streamlit as st
import pandas as pd

def show():
    """Display the events page"""
    st.header("📅 Database Events Management")
    
    if not st.session_state.get('connected'):
        st.error("Please connect to a database first")
        return
    
    db_conn = st.session_state.db_connection
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📅 Scheduled Events", "⚡ Event Triggers", "📊 Event Monitoring"])
    
    with tab1:
        show_scheduled_events(db_conn)
    
    with tab2:
        show_event_triggers(db_conn)
    
    with tab3:
        show_event_monitoring(db_conn)

def show_scheduled_events(db_conn):
    """Display scheduled events (PostgreSQL doesn't have MySQL-style events, so we show related scheduling info)"""
    st.subheader("📅 Scheduled Events")
    
    st.info("""
    **Note:** PostgreSQL doesn't have built-in scheduled events like MySQL. 
    However, you can use external schedulers like cron or pg_cron extension for scheduled tasks.
    """)
    
    try:
        # Check if pg_cron extension is available
        cron_check_query = """
        SELECT EXISTS(
            SELECT 1 FROM pg_extension WHERE extname = 'pg_cron'
        ) as pg_cron_installed
        """
        
        cron_result = db_conn.execute_query(cron_check_query)
        
        if not cron_result.empty and cron_result.iloc[0, 0]:
            st.success("✅ pg_cron extension is installed!")
            show_pg_cron_jobs(db_conn)
        else:
            st.warning("⚠️ pg_cron extension is not installed.")
            show_scheduling_alternatives()
    
    except Exception as e:
        st.error(f"Error checking for pg_cron: {str(e)}")
        show_scheduling_alternatives()

def show_pg_cron_jobs(db_conn):
    """Display pg_cron scheduled jobs"""
    try:
        # Get pg_cron jobs
        cron_jobs_query = """
        SELECT 
            jobid,
            schedule,
            command,
            nodename,
            nodeport,
            database,
            username,
            active
        FROM cron.job
        ORDER BY jobid
        """
        
        jobs_df = db_conn.execute_query(cron_jobs_query)
        
        if not jobs_df.empty:
            st.subheader("🔄 Active Cron Jobs")
            
            st.dataframe(
                jobs_df,
                column_config={
                    'jobid': st.column_config.NumberColumn('Job ID'),
                    'schedule': 'Schedule',
                    'command': 'Command',
                    'database': 'Database',
                    'username': 'User',
                    'active': 'Active'
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Jobs", len(jobs_df))
            
            with col2:
                active_jobs = len(jobs_df[jobs_df['active'] == True])
                st.metric("Active Jobs", active_jobs)
            
            with col3:
                unique_schedules = jobs_df['schedule'].nunique()
                st.metric("Unique Schedules", unique_schedules)
            
            # Show job run history
            st.subheader("📊 Job Run History")
            show_cron_job_history(db_conn)
        else:
            st.info("No scheduled jobs found")
    
    except Exception as e:
        st.error(f"Error loading pg_cron jobs: {str(e)}")

def show_cron_job_history(db_conn):
    """Display pg_cron job execution history"""
    try:
        history_query = """
        SELECT 
            jobid,
            runid,
            job_pid,
            database,
            username,
            command,
            status,
            return_message,
            start_time,
            end_time
        FROM cron.job_run_details
        ORDER BY start_time DESC
        LIMIT 50
        """
        
        history_df = db_conn.execute_query(history_query)
        
        if not history_df.empty:
            st.dataframe(
                history_df[['jobid', 'database', 'status', 'start_time', 'end_time', 'return_message']],
                column_config={
                    'jobid': st.column_config.NumberColumn('Job ID'),
                    'database': 'Database',
                    'status': 'Status',
                    'start_time': 'Started',
                    'end_time': 'Ended',
                    'return_message': 'Message'
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No job execution history found")
    
    except Exception as e:
        st.error(f"Error loading job history: {str(e)}")

def show_scheduling_alternatives():
    """Show alternatives for scheduling in PostgreSQL"""
    st.subheader("🛠️ Scheduling Alternatives")
    
    with st.expander("📚 Learn about PostgreSQL Scheduling Options"):
        st.markdown("""
        ### 1. **pg_cron Extension**
        Install the pg_cron extension to add cron-like scheduling to PostgreSQL:
        ```sql
        CREATE EXTENSION pg_cron;
        
        -- Schedule a job to run every minute
        SELECT cron.schedule('my-job', '* * * * *', 'DELETE FROM old_logs WHERE created_at < NOW() - INTERVAL ''1 day'';');
        ```
        
        ### 2. **System Cron**
        Use the system's cron scheduler:
        ```bash
        # Edit crontab
        crontab -e
        
        # Add a job to run daily at 2 AM
        0 2 * * * psql -d mydb -c "DELETE FROM old_logs WHERE created_at < NOW() - INTERVAL '1 day';"
        ```
        
        ### 3. **Application-level Scheduling**
        - Use task schedulers in your application (Celery, APScheduler, etc.)
        - Implement background job processors
        - Use cloud-based schedulers (AWS EventBridge, Google Cloud Scheduler)
        
        ### 4. **pgAgent (PostgreSQL Job Scheduler)**
        Install pgAgent for GUI-based job scheduling with pgAdmin.
        """)

def show_event_triggers(db_conn):
    """Display event triggers"""
    st.subheader("⚡ Event Triggers")
    
    try:
        # Get event triggers
        event_triggers_query = """
        SELECT 
            evtname as trigger_name,
            evtevent as event_type,
            evtowner::regrole as owner,
            evtenabled as enabled,
            evttags as tags,
            evtfoid::regprocedure as function_name
        FROM pg_event_trigger
        ORDER BY evtname
        """
        
        triggers_df = db_conn.execute_query(event_triggers_query)
        
        if not triggers_df.empty:
            st.dataframe(
                triggers_df,
                column_config={
                    'trigger_name': 'Trigger Name',
                    'event_type': 'Event Type',
                    'owner': 'Owner',
                    'enabled': 'Enabled',
                    'tags': 'Tags',
                    'function_name': 'Function'
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Event Triggers", len(triggers_df))
            
            with col2:
                enabled_count = len(triggers_df[triggers_df['enabled'] == 'O'])
                st.metric("Enabled Triggers", enabled_count)
            
            with col3:
                unique_events = triggers_df['event_type'].nunique()
                st.metric("Event Types", unique_events)
            
            # Event types distribution
            if len(triggers_df) > 0:
                import plotly.express as px
                
                event_counts = triggers_df['event_type'].value_counts()
                
                fig = px.pie(
                    values=event_counts.values,
                    names=event_counts.index,
                    title="Event Triggers by Type"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No event triggers found")
            
            # Show information about event triggers
            with st.expander("📚 Learn about Event Triggers"):
                st.markdown("""
                ### Event Triggers in PostgreSQL
                
                Event triggers are special triggers that fire on database-wide events:
                
                **Supported Events:**
                - `ddl_command_start` - Before DDL commands
                - `ddl_command_end` - After DDL commands  
                - `table_rewrite` - During table rewrites
                - `sql_drop` - Before DROP commands
                
                **Example:**
                ```sql
                -- Create a function for the event trigger
                CREATE OR REPLACE FUNCTION log_ddl_commands()
                RETURNS event_trigger AS $$
                BEGIN
                    INSERT INTO ddl_log (event_time, command_tag)
                    VALUES (NOW(), TG_TAG);
                END;
                $$ LANGUAGE plpgsql;
                
                -- Create the event trigger
                CREATE EVENT TRIGGER log_ddl
                ON ddl_command_end
                EXECUTE FUNCTION log_ddl_commands();
                ```
                """)
    
    except Exception as e:
        st.error(f"Error loading event triggers: {str(e)}")

def show_event_monitoring(db_conn):
    """Display event monitoring information"""
    st.subheader("📊 Event Monitoring")
    
    st.info("""
    Event monitoring in PostgreSQL includes:
    - Database activity logs
    - Event trigger execution history
    - System event tracking
    - Performance monitoring for events
    """)
    
    # Show basic event monitoring information
    try:
        # Check for event trigger activity
        activity_query = """
        SELECT 
            schemaname,
            tablename,
            n_tup_ins + n_tup_upd + n_tup_del as total_operations
        FROM pg_stat_user_tables
        WHERE n_tup_ins + n_tup_upd + n_tup_del > 0
        ORDER BY total_operations DESC
        LIMIT 10
        """
        
        activity_df = db_conn.execute_query(activity_query)
        
        if not activity_df.empty:
            st.subheader("📈 Most Active Tables")
            st.dataframe(
                activity_df,
                column_config={
                    'schemaname': 'Schema',
                    'tablename': 'Table',
                    'total_operations': st.column_config.NumberColumn('Operations', format="%d")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No table activity data available")
    
    except Exception as e:
        st.error(f"Error loading event monitoring: {str(e)}")
                