import streamlit as st
import psycopg2
import os
from database.connection import DatabaseConnection
from pages import dashboard, tables, functions, procedures, triggers, events, dcl_operations, query_executor, erd
from utils.helpers import init_session_state

# Configure page
st.set_page_config(
    page_title="PostgreSQL Database Manager",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    init_session_state()
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1f77b4, #2e8b57);
        color: white;
        margin-bottom: 2rem;
        border-radius: 10px;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    #stSidebarNav{
        display.none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<div class="main-header"><h1>🗄️ PostgreSQL Database Manager</h1></div>', unsafe_allow_html=True)
    
    # Sidebar for navigation and connection
    with st.sidebar:
        # Connection form
        if not st.session_state.get('connected', False):
            st.header("🔧 Database Connection")
            show_connection_form()
        else:
            st.header("🔧 Database Connection")
            show_connection_status()
            
            # Navigation menu
            st.header("📊 Navigation")
            show_navigation_menu()
    
    # Main content area
    if st.session_state.get('connected', False):
        show_main_content()
    else:
        show_welcome_screen()

def show_connection_form():
    """Display database connection form"""
    with st.form("connection_form"):
        st.subheader("Database Connection")
        
        # Get default values from environment or use fallbacks
        default_host = os.getenv("PGHOST", "localhost")
        default_port = os.getenv("PGPORT", "5432")
        default_user = os.getenv("PGUSER", "postgres")
        default_password = os.getenv("PGPASSWORD", "password")
        
        host = st.text_input("Host", value=default_host)
        port = st.text_input("Port", value=default_port)
        user = st.text_input("Username", value=default_user)
        password = st.text_input("Password", value=default_password, type="password")
        
        connect_button = st.form_submit_button("🔌 Connect", use_container_width=True)
        
        if connect_button:
            try:
                # Create database connection
                db_conn = DatabaseConnection(host, port, user, password)
                
                # Test connection
                if db_conn.test_connection():
                    st.session_state.db_connection = db_conn
                    st.session_state.connected = True
                    st.session_state.connection_params = {
                        'host': host,
                        'port': port,
                        'user': user
                    }
                    st.success("✅ Connected successfully!")
                    st.rerun()
                else:
                    st.error("❌ Connection failed!")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")

def show_connection_status():
    """Display current connection status and database selector"""
    params = st.session_state.connection_params
    st.success(f"✅ Connected to {params['host']}:{params['port']}")
    st.write(f"👤 User: {params['user']}")
    
    # Database selector
    try:
        databases = st.session_state.db_connection.get_databases()
        
        current_db = st.session_state.get('current_database', databases[0] if databases else None)
        
        selected_db = st.selectbox(
            "📁 Select Database",
            databases,
            index=databases.index(current_db) if current_db in databases else 0
        )
        
        if selected_db != st.session_state.get('current_database'):
            st.session_state.current_database = selected_db
            st.session_state.db_connection.connect_to_database(selected_db)
            st.rerun()
            
    except Exception as e:
        st.error(f"Error loading databases: {str(e)}")
    
    # Disconnect button
    if st.button("🔌 Disconnect", use_container_width=True):
        st.session_state.connected = False
        st.session_state.db_connection = None
        st.session_state.current_database = None
        st.rerun()

def show_navigation_menu():
    """Display navigation menu"""
    menu_items = [
        ("📊 Dashboard", "dashboard"),
        ("🗂️ Tables", "tables"),
        ("🔗 ERD Diagram", "erd"),
        ("⚙️ Functions", "functions"),
        ("🔧 Procedures", "procedures"),
        ("⚡ Triggers", "triggers"),
        ("📅 Events", "events"),
        ("🔐 DCL Operations", "dcl_operations"),
        ("💻 Query Executor", "query_executor")
    ]
    
    current_page = st.session_state.get('current_page', 'dashboard')
    
    for label, page_key in menu_items:
        if st.button(label, use_container_width=True, 
                    type="primary" if current_page == page_key else "secondary"):
            st.session_state.current_page = page_key
            st.rerun()

def show_main_content():
    """Display main content based on selected page"""
    current_page = st.session_state.get('current_page', 'dashboard')
    
    # Page routing
    if current_page == 'dashboard':
        dashboard.show()
    elif current_page == 'tables':
        tables.show()
    elif current_page == 'functions':
        functions.show()
    elif current_page == 'procedures':
        procedures.show()
    elif current_page == 'triggers':
        triggers.show()
    elif current_page == 'events':
        events.show()
    elif current_page == 'dcl_operations':
        dcl_operations.show()
    elif current_page == 'query_executor':
        query_executor.show()
    elif current_page == 'erd':
        erd.show()

def show_welcome_screen():
    """Display welcome screen when not connected"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ## 🎉 Welcome to PostgreSQL Database Manager
        
        This comprehensive database management tool provides:
        
        ### 🔍 **Database Exploration**
        - View all tables, views, indexes, and sequences
        - Browse functions and stored procedures
        - Monitor triggers and events
        - Analyze database structure and relationships
        
        ### 📊 **Interactive Dashboard**
        - Real-time database statistics
        - Visual charts and metrics
        - Performance monitoring
        - Storage usage analysis
        
        ### 🔐 **DCL Operations**
        - User and role management
        - Grant/Revoke privileges
        - Permission viewing
        - Security administration
        
        ### 💻 **Query Execution**
        - Interactive SQL editor
        - Query result visualization
        - Error handling and validation
        - Query history tracking
        
        ---
        
        **👈 Please connect to your PostgreSQL database using the sidebar to get started.**
        """)

if __name__ == "__main__":
    main()
