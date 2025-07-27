import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import networkx as nx
from database import DatabaseConnection
from utils import format_number

st.set_page_config(
    page_title="Relationships - Database Explorer",
    page_icon="🔗",
    layout="wide"
)

def main():
    st.title("🔗 Database Relationships")
    st.markdown("Explore table relationships and foreign key connections")
    
    # Initialize database
    @st.cache_resource
    def init_database():
        return DatabaseConnection()
    
    db = init_database()
    
    if not db.test_connection():
        st.error("❌ Database connection failed")
        return
    
    # Get all tables and relationships
    tables = db.get_all_tables()
    relationships = db.get_table_relationships()
    
    if not tables:
        st.error("No tables found")
        return
    
    # Display relationship overview
    st.header("📊 Relationship Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tables", len(tables))
    with col2:
        st.metric("Foreign Keys", len(relationships))
    with col3:
        connected_tables = len(set([r['from_table'] for r in relationships] + [r['to_table'] for r in relationships]))
        st.metric("Connected Tables", connected_tables)
    with col4:
        isolated_tables = len(tables) - connected_tables
        st.metric("Isolated Tables", isolated_tables)
    
    # Relationship visualization
    st.header("🕸️ Relationship Diagram")
    
    if relationships:
        # Create network diagram
        fig = create_relationship_diagram(tables, relationships)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No foreign key relationships found in the database")
    
    # Detailed relationship table
    st.header("📋 Relationship Details")
    
    if relationships:
        # Convert relationships to DataFrame
        df_relationships = pd.DataFrame(relationships)
        df_relationships.columns = ['From Table', 'From Column', 'To Table', 'To Column']
        
        # Add relationship type
        df_relationships['Relationship'] = df_relationships.apply(
            lambda row: f"{row['From Table']}.{row['From Column']} → {row['To Table']}.{row['To Column']}", 
            axis=1
        )
        
        st.dataframe(df_relationships, use_container_width=True)
        
        # Relationship analysis
        st.subheader("🔍 Relationship Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tables with most foreign keys
            from_table_counts = df_relationships['From Table'].value_counts()
            st.write("**Tables with Most Foreign Keys:**")
            for table, count in from_table_counts.head(5).items():
                st.write(f"• {table}: {count} foreign keys")
        
        with col2:
            # Most referenced tables
            to_table_counts = df_relationships['To Table'].value_counts()
            st.write("**Most Referenced Tables:**")
            for table, count in to_table_counts.head(5).items():
                st.write(f"• {table}: referenced {count} times")
    
    # Individual table relationships
    st.header("🔍 Table-Specific Relationships")
    
    selected_table = st.selectbox("Select a table to explore:", tables)
    
    if selected_table:
        show_table_relationships(db, selected_table, relationships)
    
    # Data integrity checks
    st.header("✅ Data Integrity Checks")
    
    if st.button("Run Integrity Checks"):
        run_integrity_checks(db, relationships)

def create_relationship_diagram(tables, relationships):
    """Create a network diagram showing table relationships"""
    # Create a graph
    G = nx.Graph()
    
    # Add all tables as nodes
    for table in tables:
        G.add_node(table)
    
    # Add relationships as edges
    for rel in relationships:
        G.add_edge(rel['from_table'], rel['to_table'])
    
    # Calculate layout
    try:
        pos = nx.spring_layout(G, k=3, iterations=50)
    except:
        # Fallback to circular layout if spring layout fails
        pos = nx.circular_layout(G)
    
    # Create edge traces
    edge_x = []
    edge_y = []
    edge_info = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # Find the relationship details
        rel_details = [r for r in relationships if 
                      (r['from_table'] == edge[0] and r['to_table'] == edge[1]) or
                      (r['from_table'] == edge[1] and r['to_table'] == edge[0])]
        if rel_details:
            edge_info.append(f"{rel_details[0]['from_table']}.{rel_details[0]['from_column']} → {rel_details[0]['to_table']}.{rel_details[0]['to_column']}")
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_info = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        
        # Count connections
        connections = len([r for r in relationships if r['from_table'] == node or r['to_table'] == node])
        node_info.append(f"Table: {node}<br>Connections: {connections}")
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="middle center",
        hovertext=node_info,
        marker=dict(
            size=30,
            color=[len([r for r in relationships if r['from_table'] == node or r['to_table'] == node]) for node in G.nodes()],
            colorscale='Viridis',
            colorbar=dict(
                thickness=15,
                len=0.5,
                x=1.02,
                title="Connections"
            ),
            line=dict(width=2, color='white')
        )
    )
    
    # Create the figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title='Database Table Relationships',
                    #    titlefont_size=16,
                        font=dict(size=16),
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       annotations=[ dict(
                           text="Node size indicates number of connections",
                           showarrow=False,
                           xref="paper", yref="paper",
                           x=0.005, y=-0.002,
                           xanchor="left", yanchor="bottom",
                           font=dict(color="#888", size=12)
                       )],
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=600
                   ))
    
    return fig

def show_table_relationships(db, table_name, all_relationships):
    """Show relationships for a specific table"""
    # Get relationships where this table is involved
    table_relationships = [r for r in all_relationships if 
                          r['from_table'] == table_name or r['to_table'] == table_name]
    
    if not table_relationships:
        st.info(f"Table '{table_name}' has no foreign key relationships")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔗 Outgoing References (Foreign Keys)")
        outgoing = [r for r in table_relationships if r['from_table'] == table_name]
        
        if outgoing:
            for rel in outgoing:
                st.write(f"• **{rel['from_column']}** → {rel['to_table']}.{rel['to_column']}")
                
                # Show sample data for this relationship
                if st.button(f"View {rel['from_column']} data", key=f"out_{rel['from_column']}"):
                    sample_data = db.execute_query(
                        f"SELECT {rel['from_column']}, COUNT(*) as count FROM `{table_name}` "
                        f"GROUP BY {rel['from_column']} ORDER BY count DESC LIMIT 10"
                    )
                    if not sample_data.empty:
                        st.dataframe(sample_data, use_container_width=True)
        else:
            st.info("No outgoing references")
    
    with col2:
        st.subheader("⬅️ Incoming References")
        incoming = [r for r in table_relationships if r['to_table'] == table_name]
        
        if incoming:
            for rel in incoming:
                st.write(f"• {rel['from_table']}.{rel['from_column']} → **{rel['to_column']}**")
                
                # Show sample data for this relationship
                if st.button(f"View {rel['from_table']} data", key=f"in_{rel['from_table']}"):
                    sample_data = db.execute_query(
                        f"SELECT {rel['from_column']}, COUNT(*) as count FROM `{rel['from_table']}` "
                        f"GROUP BY {rel['from_column']} ORDER BY count DESC LIMIT 10"
                    )
                    if not sample_data.empty:
                        st.dataframe(sample_data, use_container_width=True)
        else:
            st.info("No incoming references")
    
    # Show related data
    st.subheader("📊 Related Data Analysis")
    
    if outgoing:
        selected_relation = st.selectbox(
            "Select a relationship to analyze:",
            [f"{r['from_column']} → {r['to_table']}" for r in outgoing]
        )
        
        if selected_relation:
            # Parse the selected relationship
            from_col = selected_relation.split(' → ')[0]
            to_table = selected_relation.split(' → ')[1]
            
            # Find the relationship details
            rel_detail = next(r for r in outgoing if r['from_column'] == from_col and r['to_table'] == to_table)
            
            # Show join query results
            join_query = f"""
            SELECT t1.{from_col}, t2.*, COUNT(*) as usage_count
            FROM `{table_name}` t1
            JOIN `{to_table}` t2 ON t1.{from_col} = t2.{rel_detail['to_column']}
            GROUP BY t1.{from_col}
            ORDER BY usage_count DESC
            LIMIT 20
            """
            
            join_data = db.execute_query(join_query)
            if not join_data.empty:
                st.dataframe(join_data, use_container_width=True)

def run_integrity_checks(db, relationships):
    """Run data integrity checks for foreign key relationships"""
    st.subheader("🔍 Running Integrity Checks...")
    
    issues_found = 0
    
    for rel in relationships:
        from_table = rel['from_table']
        from_col = rel['from_column']
        to_table = rel['to_table']
        to_col = rel['to_column']
        
        # Check for orphaned records
        orphan_query = f"""
        SELECT COUNT(*) as orphan_count
        FROM `{from_table}` t1
        LEFT JOIN `{to_table}` t2 ON t1.{from_col} = t2.{to_col}
        WHERE t1.{from_col} IS NOT NULL AND t2.{to_col} IS NULL
        """
        
        orphan_result = db.execute_query(orphan_query)
        
        if not orphan_result.empty:
            orphan_count = orphan_result.iloc[0, 0]
            
            if orphan_count > 0:
                st.warning(f"⚠️ Found {orphan_count} orphaned records in {from_table}.{from_col} → {to_table}.{to_col}")
                issues_found += 1
            else:
                st.success(f"✅ {from_table}.{from_col} → {to_table}.{to_col}: No integrity issues")
    
    if issues_found == 0:
        st.success("🎉 All foreign key relationships are clean!")
    else:
        st.error(f"Found {issues_found} integrity issues that need attention")

if __name__ == "__main__":
    main()
