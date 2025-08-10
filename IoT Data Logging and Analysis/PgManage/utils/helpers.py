import streamlit as st

def init_session_state():
    """Initialize session state variables"""
    
    # Connection state
    if 'connected' not in st.session_state:
        st.session_state.connected = False
    
    if 'db_connection' not in st.session_state:
        st.session_state.db_connection = None
    
    if 'current_database' not in st.session_state:
        st.session_state.current_database = None
    
    if 'connection_params' not in st.session_state:
        st.session_state.connection_params = {}
    
    # Navigation state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    # Query history for query executor
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    # Dashboard auto-refresh state
    if 'dashboard_auto_refresh' not in st.session_state:
        st.session_state.dashboard_auto_refresh = False

def format_bytes(bytes_value):
    """Format bytes into human readable format"""
    if bytes_value is None:
        return "N/A"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def format_number(number):
    """Format large numbers with commas"""
    if number is None:
        return "N/A"
    
    try:
        return f"{int(number):,}"
    except (ValueError, TypeError):
        return str(number)

def safe_execute(func, default_value=None, error_message="Operation failed"):
    """Safely execute a function and handle errors"""
    try:
        return func()
    except Exception as e:
        st.error(f"{error_message}: {str(e)}")
        return default_value

def validate_sql_query(query):
    """Basic SQL query validation"""
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    # Remove comments and whitespace
    clean_query = query.strip()
    
    # Check for obvious injection attempts (basic check)
    dangerous_patterns = [
        '; DROP ', '; DELETE ', '; UPDATE ', '; INSERT ',
        '/*', '*/', '--', 'xp_', 'sp_'
    ]
    
    query_upper = clean_query.upper()
    for pattern in dangerous_patterns:
        if pattern in query_upper:
            return False, f"Potentially dangerous pattern detected: {pattern}"
    
    return True, "Query appears safe"

def get_connection_string(host, port, user, password, database):
    """Generate connection string for display purposes (without password)"""
    return f"postgresql://{user}:***@{host}:{port}/{database}"

def truncate_string(text, max_length=50):
    """Truncate string with ellipsis if too long"""
    if text is None:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    if seconds is None:
        return "N/A"
    
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def get_table_color(table_type):
    """Get color coding for different table types"""
    colors = {
        'BASE TABLE': '#1f77b4',
        'VIEW': '#ff7f0e',
        'MATERIALIZED VIEW': '#2ca02c',
        'FOREIGN TABLE': '#d62728'
    }
    return colors.get(table_type, '#7f7f7f')

def format_privilege_display(privilege_type):
    """Format privilege type for better display"""
    privilege_icons = {
        'SELECT': '👁️ SELECT',
        'INSERT': '➕ INSERT',
        'UPDATE': '✏️ UPDATE',
        'DELETE': '🗑️ DELETE',
        'TRUNCATE': '🔄 TRUNCATE',
        'REFERENCES': '🔗 REFERENCES',
        'TRIGGER': '⚡ TRIGGER',
        'CREATE': '🏗️ CREATE',
        'USAGE': '🔑 USAGE',
        'EXECUTE': '▶️ EXECUTE'
    }
    return privilege_icons.get(privilege_type.upper(), f"🔒 {privilege_type}")

def check_database_version(db_connection):
    """Check PostgreSQL version"""
    try:
        result = db_connection.execute_query("SELECT version()")
        if not result.empty:
            version_string = result.iloc[0, 0]
            return version_string
    except:
        pass
    return "Unknown"

def get_database_encoding(db_connection):
    """Get database encoding"""
    try:
        result = db_connection.execute_query("SHOW server_encoding")
        if not result.empty:
            return result.iloc[0, 0]
    except:
        pass
    return "Unknown"

def cleanup_session_state():
    """Clean up session state when disconnecting"""
    keys_to_remove = [
        'connected', 'db_connection', 'current_database', 
        'connection_params', 'query_history'
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

def export_data_to_csv(dataframe, filename_prefix="data"):
    """Export dataframe to CSV with proper formatting"""
    try:
        import io
        import datetime
        
        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        
        # Convert dataframe to CSV
        csv_buffer = io.StringIO()
        dataframe.to_csv(csv_buffer, index=False)
        csv_string = csv_buffer.getvalue()
        
        return csv_string, filename
    except Exception as e:
        st.error(f"Error exporting data: {str(e)}")
        return None, None

def display_error_with_details(error, context="Operation"):
    """Display detailed error information"""
    st.error(f"❌ {context} failed")
    
    with st.expander("Error Details"):
        st.write(f"**Error Type:** {type(error).__name__}")
        st.write(f"**Error Message:** {str(error)}")
        
        # Additional context for common PostgreSQL errors
        error_str = str(error).lower()
        
        if "permission denied" in error_str:
            st.info("💡 **Suggestion:** Check if you have the required privileges for this operation")
        elif "relation does not exist" in error_str:
            st.info("💡 **Suggestion:** Verify that the table/view name is correct and exists")
        elif "syntax error" in error_str:
            st.info("💡 **Suggestion:** Check your SQL syntax for any typos or missing keywords")
        elif "connection" in error_str:
            st.info("💡 **Suggestion:** Check your database connection settings and network connectivity")

def show_loading_spinner(message="Loading..."):
    """Show loading spinner with custom message"""
    return st.spinner(message)

def create_info_card(title, value, delta=None, delta_color=None):
    """Create an information card display"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if delta_color:
            st.metric(
                label=title,
                value=value,
                delta=delta,
                delta_color=delta_color
            )
        else:
            st.metric(
                label=title,
                value=value,
                delta=delta
            )

def format_sql_for_display(sql_query, max_lines=10):
    """Format SQL query for better display"""
    if not sql_query:
        return ""
    
    lines = sql_query.split('\n')
    
    if len(lines) > max_lines:
        displayed_lines = lines[:max_lines]
        displayed_lines.append(f"... ({len(lines) - max_lines} more lines)")
        return '\n'.join(displayed_lines)
    
    return sql_query
