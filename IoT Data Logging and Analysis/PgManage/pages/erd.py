import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def show():
    """Display the ERD (Entity Relationship Diagram) page"""
    st.header("🔗 Entity Relationship Diagram (ERD)")
    
    if not st.session_state.get('connected'):
        st.error("Please connect to a database first")
        return
    
    db_conn = st.session_state.db_connection
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📊 Table Relationships", "📋 Schema Overview", "🔍 Relationship Details"])
    
    with tab1:
        show_erd_diagram(db_conn)
    
    with tab2:
        show_schema_overview(db_conn)
    
    with tab3:
        show_relationship_details(db_conn)

def show_erd_diagram(db_conn):
    """Display interactive ERD diagram"""
    st.subheader("📊 Database Relationships")
    
    try:
        # Get all tables and their relationships
        tables_query = """
        SELECT 
            t.table_schema,
            t.table_name,
            COUNT(c.column_name) as column_count
        FROM information_schema.tables t
        LEFT JOIN information_schema.columns c 
            ON t.table_schema = c.table_schema 
            AND t.table_name = c.table_name
        WHERE t.table_type = 'BASE TABLE'
            AND t.table_schema NOT IN ('information_schema', 'pg_catalog')
        GROUP BY t.table_schema, t.table_name
        ORDER BY t.table_schema, t.table_name
        """
        
        tables_df = db_conn.execute_query(tables_query)
        
        if tables_df.empty:
            st.info("No tables found in the current database")
            return
        
        # Get foreign key relationships
        fk_query = """
        SELECT 
            tc.table_schema as source_schema,
            tc.table_name as source_table,
            kcu.column_name as source_column,
            ccu.table_schema as target_schema,
            ccu.table_name as target_table,
            ccu.column_name as target_column,
            tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema NOT IN ('information_schema', 'pg_catalog')
        """
        
        fk_df = db_conn.execute_query(fk_query)
        
        # Create interactive diagram
        fig = create_erd_visualization(tables_df, fk_df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show relationships summary
        if not fk_df.empty:
            st.subheader("🔗 Relationship Summary")
            
            relationship_summary = fk_df.groupby(['source_table', 'target_table']).size().reset_index(name='relationship_count')
            
            st.dataframe(
                relationship_summary,
                column_config={
                    'source_table': 'Source Table',
                    'target_table': 'Target Table',
                    'relationship_count': st.column_config.NumberColumn('Relationships', format="%d")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No foreign key relationships found")
    
    except Exception as e:
        st.error(f"Error creating ERD: {str(e)}")

def create_erd_visualization(tables_df, fk_df):
    """Create interactive ERD visualization using Plotly"""
    fig = go.Figure()
    
    # Position tables in a grid layout
    import math
    num_tables = len(tables_df)
    cols = math.ceil(math.sqrt(num_tables))
    rows = math.ceil(num_tables / cols)
    
    table_positions = {}
    
    for i, (_, table) in enumerate(tables_df.iterrows()):
        row = i // cols
        col = i % cols
        
        x = col * 200 + 100
        y = row * 150 + 100
        
        table_name = f"{table['table_schema']}.{table['table_name']}"
        table_positions[table_name] = (x, y)
        
        # Add table rectangle
        fig.add_shape(
            type="rect",
            x0=x-60, y0=y-30, x1=x+60, y1=y+30,
            line=dict(color="RoyalBlue", width=2),
            fillcolor="LightBlue",
            opacity=0.7
        )
        
        # Add table name
        fig.add_annotation(
            x=x, y=y,
            text=f"<b>{table['table_name']}</b><br>{table['column_count']} columns",
            showarrow=False,
            font=dict(size=10, color="DarkBlue"),
            bgcolor="white",
            bordercolor="blue",
            borderwidth=1
        )
    
    # Add relationship lines
    if not fk_df.empty:
        for _, fk in fk_df.iterrows():
            source_table = f"{fk['source_schema']}.{fk['source_table']}"
            target_table = f"{fk['target_schema']}.{fk['target_table']}"
            
            if source_table in table_positions and target_table in table_positions:
                x1, y1 = table_positions[source_table]
                x2, y2 = table_positions[target_table]
                
                fig.add_shape(
                    type="line",
                    x0=x1, y0=y1, x1=x2, y1=y2,
                    line=dict(color="Red", width=2, dash="dash"),
                    opacity=0.6
                )
    
    # Update layout
    fig.update_layout(
        title="Database Entity Relationship Diagram",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

def show_schema_overview(db_conn):
    """Display schema overview with statistics"""
    st.subheader("📋 Schema Overview")
    
    try:
        # Get schema statistics
        schema_query = """
        SELECT 
            table_schema,
            COUNT(DISTINCT table_name) as table_count,
            COUNT(column_name) as total_columns,
            COUNT(DISTINCT CASE WHEN data_type LIKE '%char%' OR data_type = 'text' THEN column_name END) as text_columns,
            COUNT(DISTINCT CASE WHEN data_type IN ('integer', 'bigint', 'smallint', 'numeric', 'decimal', 'real', 'double precision') THEN column_name END) as numeric_columns,
            COUNT(DISTINCT CASE WHEN data_type LIKE '%timestamp%' OR data_type = 'date' THEN column_name END) as date_columns
        FROM information_schema.tables t
        JOIN information_schema.columns c USING (table_schema, table_name)
        WHERE table_type = 'BASE TABLE'
            AND table_schema NOT IN ('information_schema', 'pg_catalog')
        GROUP BY table_schema
        ORDER BY table_count DESC
        """
        
        schema_df = db_conn.execute_query(schema_query)
        
        if not schema_df.empty:
            # Display schema statistics
            st.dataframe(
                schema_df,
                column_config={
                    'table_schema': 'Schema',
                    'table_count': st.column_config.NumberColumn('Tables', format="%d"),
                    'total_columns': st.column_config.NumberColumn('Total Columns', format="%d"),
                    'text_columns': st.column_config.NumberColumn('Text Columns', format="%d"),
                    'numeric_columns': st.column_config.NumberColumn('Numeric Columns', format="%d"),
                    'date_columns': st.column_config.NumberColumn('Date Columns', format="%d")
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Create visualization
            fig = px.bar(
                schema_df, 
                x='table_schema', 
                y='table_count',
                title="Tables per Schema",
                labels={'table_schema': 'Schema', 'table_count': 'Number of Tables'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No schema information available")
    
    except Exception as e:
        st.error(f"Error loading schema overview: {str(e)}")

def show_relationship_details(db_conn):
    """Display detailed relationship information"""
    st.subheader("🔍 Relationship Details")
    
    try:
        # Get detailed foreign key information
        detailed_fk_query = """
        SELECT 
            tc.table_schema || '.' || tc.table_name as source_table,
            kcu.column_name as source_column,
            ccu.table_schema || '.' || ccu.table_name as target_table,
            ccu.column_name as target_column,
            tc.constraint_name,
            rc.update_rule,
            rc.delete_rule
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        JOIN information_schema.referential_constraints rc
            ON tc.constraint_name = rc.constraint_name
            AND tc.table_schema = rc.constraint_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY tc.table_schema, tc.table_name, kcu.column_name
        """
        
        detailed_fk_df = db_conn.execute_query(detailed_fk_query)
        
        if not detailed_fk_df.empty:
            # Search functionality
            search_term = st.text_input("🔍 Search relationships", placeholder="Enter table or column name...")
            
            if search_term:
                filtered_df = detailed_fk_df[
                    detailed_fk_df['source_table'].str.contains(search_term, case=False, na=False) |
                    detailed_fk_df['target_table'].str.contains(search_term, case=False, na=False) |
                    detailed_fk_df['source_column'].str.contains(search_term, case=False, na=False) |
                    detailed_fk_df['target_column'].str.contains(search_term, case=False, na=False)
                ]
            else:
                filtered_df = detailed_fk_df
            
            st.dataframe(
                filtered_df,
                column_config={
                    'source_table': 'Source Table',
                    'source_column': 'Source Column',
                    'target_table': 'Target Table',
                    'target_column': 'Target Column',
                    'constraint_name': 'Constraint Name',
                    'update_rule': 'Update Rule',
                    'delete_rule': 'Delete Rule'
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Show constraint rules summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Update Rules")
                update_rules = detailed_fk_df['update_rule'].value_counts()
                fig_update = px.pie(values=update_rules.values, names=update_rules.index, title="Update Rules Distribution")
                st.plotly_chart(fig_update, use_container_width=True)
            
            with col2:
                st.subheader("Delete Rules")
                delete_rules = detailed_fk_df['delete_rule'].value_counts()
                fig_delete = px.pie(values=delete_rules.values, names=delete_rules.index, title="Delete Rules Distribution")
                st.plotly_chart(fig_delete, use_container_width=True)
        else:
            st.info("No foreign key relationships found in the database")
            
            # Show information about creating relationships
            with st.expander("📚 Learn about Foreign Key Relationships"):
                st.markdown("""
                ### Foreign Key Relationships in PostgreSQL
                
                Foreign keys are used to link data between tables and ensure referential integrity.
                
                **Creating a Foreign Key:**
                ```sql
                ALTER TABLE child_table 
                ADD CONSTRAINT fk_name 
                FOREIGN KEY (child_column) 
                REFERENCES parent_table(parent_column);
                ```
                
                **Constraint Rules:**
                - **CASCADE**: Automatically update/delete related records
                - **RESTRICT**: Prevent update/delete if related records exist
                - **SET NULL**: Set foreign key to NULL when parent is updated/deleted
                - **SET DEFAULT**: Set foreign key to default value
                - **NO ACTION**: Same as RESTRICT but can be deferred
                """)
    
    except Exception as e:
        st.error(f"Error loading relationship details: {str(e)}")