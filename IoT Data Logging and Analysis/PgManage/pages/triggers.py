import streamlit as st
import pandas as pd
from database.queries import TRIGGER_QUERIES

def show():
    """Display the triggers page"""
    st.header("⚡ Triggers Management")
    
    if not st.session_state.get('connected'):
        st.error("Please connect to a database first")
        return
    
    db_conn = st.session_state.db_connection
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["⚡ Table Triggers", "📅 Event Triggers", "🔍 Trigger Details"])
    
    with tab1:
        show_table_triggers(db_conn)
    
    with tab2:
        show_event_triggers(db_conn)
    
    with tab3:
        show_trigger_details(db_conn)

def show_table_triggers(db_conn):
    """Display all table triggers"""
    st.subheader("⚡ Table Triggers")
    
    try:
        # Get all table triggers
        triggers_df = db_conn.execute_query(TRIGGER_QUERIES['all_triggers'])
        
        if not triggers_df.empty:
            # Search functionality
            search_term = st.text_input("🔍 Search triggers", placeholder="Enter trigger name, table, or schema...")
            
            if search_term:
                filtered_df = triggers_df[
                    triggers_df['trigger_name'].str.contains(search_term, case=False, na=False) |
                    triggers_df['event_object_table'].str.contains(search_term, case=False, na=False) |
                    triggers_df['trigger_schema'].str.contains(search_term, case=False, na=False)
                ]
            else:
                filtered_df = triggers_df
            
            # Filter by event type
            col1, col2 = st.columns(2)
            
            with col1:
                event_types = triggers_df['event_manipulation'].unique()
                selected_event = st.selectbox("Filter by event", ['All'] + list(event_types))
            
            with col2:
                timing_types = triggers_df['action_timing'].unique()
                selected_timing = st.selectbox("Filter by timing", ['All'] + list(timing_types))
            
            if selected_event != 'All':
                filtered_df = filtered_df[filtered_df['event_manipulation'] == selected_event]
            
            if selected_timing != 'All':
                filtered_df = filtered_df[filtered_df['action_timing'] == selected_timing]
            
            # Display triggers
            st.dataframe(
                filtered_df[['trigger_schema', 'trigger_name', 'event_object_table', 'event_manipulation', 'action_timing', 'action_orientation']],
                column_config={
                    'trigger_schema': 'Schema',
                    'trigger_name': 'Trigger Name',
                    'event_object_table': 'Table',
                    'event_manipulation': 'Event',
                    'action_timing': 'Timing',
                    'action_orientation': 'Orientation'
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Triggers", len(filtered_df))
            
            with col2:
                before_triggers = len(filtered_df[filtered_df['action_timing'] == 'BEFORE'])
                st.metric("BEFORE Triggers", before_triggers)
            
            with col3:
                after_triggers = len(filtered_df[filtered_df['action_timing'] == 'AFTER'])
                st.metric("AFTER Triggers", after_triggers)
            
            with col4:
                schemas = filtered_df['trigger_schema'].nunique()
                st.metric("Schemas", schemas)
            
            # Event distribution chart
            if len(filtered_df) > 0:
                import plotly.express as px
                
                event_counts = filtered_df['event_manipulation'].value_counts()
                
                fig = px.pie(
                    values=event_counts.values,
                    names=event_counts.index,
                    title="Trigger Events Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No table triggers found in the current database")
    
    except Exception as e:
        st.error(f"Error loading table triggers: {str(e)}")

def show_event_triggers(db_conn):
    """Display all event triggers"""
    st.subheader("📅 Event Triggers")
    
    try:
        # Get all event triggers
        event_triggers_df = db_conn.execute_query(TRIGGER_QUERIES['event_triggers'])
        
        if not event_triggers_df.empty:
            # Display event triggers
            st.dataframe(
                event_triggers_df,
                column_config={
                    'trigger_name': 'Trigger Name',
                    'event': 'Event Type',
                    'owner': 'Owner',
                    'enabled': 'Enabled',
                    'tags': 'Tags'
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Event Triggers", len(event_triggers_df))
            
            with col2:
                enabled_triggers = len(event_triggers_df[event_triggers_df['enabled'] == 'O'])  # 'O' means enabled
                st.metric("Enabled Triggers", enabled_triggers)
            
            with col3:
                unique_events = event_triggers_df['event'].nunique()
                st.metric("Event Types", unique_events)
            
            # Event triggers by type
            if len(event_triggers_df) > 0:
                import plotly.express as px
                
                event_counts = event_triggers_df['event'].value_counts()
                
                fig = px.bar(
                    x=event_counts.index,
                    y=event_counts.values,
                    title="Event Triggers by Type",
                    labels={'x': 'Event Type', 'y': 'Count'}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No event triggers found in the current database")
    
    except Exception as e:
        st.error(f"Error loading event triggers: {str(e)}")

def show_trigger_details(db_conn):
    """Display detailed information about a specific trigger"""
    st.subheader("🔍 Trigger Details")
    
    try:
        # Get list of triggers for selection
        triggers_df = db_conn.execute_query(TRIGGER_QUERIES['all_triggers'])
        
        if not triggers_df.empty:
            # Trigger selection
            trigger_options = [
                f"{row['trigger_schema']}.{row['trigger_name']} (on {row['event_object_table']})"
                for _, row in triggers_df.iterrows()
            ]
            
            selected_trigger = st.selectbox("Select a trigger", trigger_options)
            
            if selected_trigger:
                # Parse selection
                parts = selected_trigger.split(' (on ')
                schema_and_name = parts[0]
                table_name = parts[1].rstrip(')')
                schema, trigger_name = schema_and_name.split('.', 1)
                
                # Get trigger details
                trigger_row = triggers_df[
                    (triggers_df['trigger_schema'] == schema) &
                    (triggers_df['trigger_name'] == trigger_name)
                ].iloc[0]
                
                # Display trigger information
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Schema:** {trigger_row['trigger_schema']}")
                    st.write(f"**Trigger Name:** {trigger_row['trigger_name']}")
                    st.write(f"**Table:** {trigger_row['event_object_table']}")
                
                with col2:
                    st.write(f"**Event:** {trigger_row['event_manipulation']}")
                    st.write(f"**Timing:** {trigger_row['action_timing']}")
                    st.write(f"**Orientation:** {trigger_row['action_orientation']}")
                
                # Show trigger definition
                st.subheader("📝 Trigger Definition")
                if pd.notna(trigger_row['action_statement']):
                    st.code(trigger_row['action_statement'], language='sql')
                else:
                    st.info("Trigger definition not available")
                
                # Show trigger function (if applicable)
                st.subheader("⚙️ Trigger Function")
                show_trigger_function(db_conn, schema, trigger_name)
                
                # Show trigger status and metadata
                st.subheader("📊 Trigger Metadata")
                show_trigger_metadata(db_conn, schema, trigger_name, table_name)
        else:
            st.info("No triggers available")
    
    except Exception as e:
        st.error(f"Error loading trigger details: {str(e)}")

def show_trigger_function(db_conn, schema, trigger_name):
    """Display trigger function details"""
    try:
        # Get trigger function information
        func_query = """
        SELECT 
            p.proname as function_name,
            n.nspname as function_schema,
            pg_get_functiondef(p.oid) as function_definition
        FROM pg_trigger t
        JOIN pg_proc p ON t.tgfoid = p.oid
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE t.tgname = %s
        """
        
        cursor = db_conn.connection.cursor()
        cursor.execute(func_query, (trigger_name,))
        function_info = cursor.fetchone()
        cursor.close()
        
        if function_info:
            function_name, function_schema, function_def = function_info
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Function Name:** {function_name}")
            
            with col2:
                st.write(f"**Function Schema:** {function_schema}")
            
            if function_def:
                st.code(function_def, language='sql')
            else:
                st.info("Function definition not available")
        else:
            st.info("Trigger function information not available")
    
    except Exception as e:
        st.error(f"Error loading trigger function: {str(e)}")

def show_trigger_metadata(db_conn, schema, trigger_name, table_name):
    """Display trigger metadata and status"""
    try:
        # Get trigger metadata
        meta_query = """
        SELECT 
            t.tgenabled as enabled,
            t.tgtype as trigger_type,
            t.tgnargs as num_args,
            t.tgargs as args
        FROM pg_trigger t
        JOIN pg_class c ON t.tgrelid = c.oid
        JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE t.tgname = %s AND n.nspname = %s AND c.relname = %s
        """
        
        cursor = db_conn.connection.cursor()
        cursor.execute(meta_query, (trigger_name, schema, table_name))
        metadata = cursor.fetchone()
        cursor.close()
        
        if metadata:
            enabled, trigger_type, num_args, args = metadata
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Decode enabled status
                enabled_status = "Enabled" if enabled == 'O' else "Disabled"
                st.write(f"**Status:** {enabled_status}")
                st.write(f"**Number of Arguments:** {num_args}")
            
            with col2:
                st.write(f"**Trigger Type Code:** {trigger_type}")
                if args:
                    st.write(f"**Arguments:** {args}")
        else:
            st.info("Trigger metadata not available")
    
    except Exception as e:
        st.error(f"Error loading trigger metadata: {str(e)}")
