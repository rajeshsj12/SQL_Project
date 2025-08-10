# PostgreSQL Database Manager

A comprehensive cross-platform Streamlit-based PostgreSQL database management web application with setup automation, full database object exploration, DCL operations, event monitoring, and interactive dashboard.

![PostgreSQL Database Manager](https://img.shields.io/badge/PostgreSQL-Database%20Manager-blue)
![Python](https://img.shields.io/badge/Python-3.7%2B-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red)

## 🚀 Features

### 🔍 Database Exploration
- **Tables Management**: View all tables with row counts, sizes, indexes, and constraints
- **Functions & Procedures**: Browse and execute stored procedures and functions with parameters
- **Triggers**: Monitor table triggers and event triggers with detailed information
- **Views & Indexes**: Explore database views and index usage statistics
- **Sequences**: Track sequence values and usage

### 📊 Interactive Dashboard
- Real-time database statistics and metrics
- Visual charts showing table sizes, row counts, and distribution
- Performance monitoring with cache hit ratios and query statistics
- Active connections and session monitoring
- Database size and storage usage tracking

### 🔐 DCL Operations (Data Control Language)
- **User & Role Management**: Create, modify, and delete database users and roles
- **Privilege Management**: Grant and revoke table, schema, and database privileges
- **Security Overview**: Monitor user privileges and security recommendations
- **Permission Viewing**: Comprehensive privilege auditing and reporting

### 💻 Query Execution
- Interactive SQL editor with syntax highlighting
- Query execution with result visualization
- Query history tracking and management
- EXPLAIN query analysis for performance optimization
- Export query results to CSV format

### 📅 Event Management
- Event triggers monitoring and management
- Scheduled events support (via pg_cron extension)
- Database event logging and tracking

## 🛠️ Installation

### Windows Installation

1. **Download and Extract**: Download the application files to a folder
2. **Run Setup**: Double-click `setup.bat` to automatically install dependencies
3. **Start Application**: Double-click `run.bat` to launch the application

### Ubuntu/Linux Installation

1. **Download and Extract**: Download the application files to a folder
2. **Make Scripts Executable**:
   ```bash
   chmod +x setup.sh run.sh
   ```
3. **Run Setup**:
   ```bash
   ./setup.sh
   ```
4. **Start Application**:
   ```bash
   ./run.sh
   ```

### Manual Installation

If you prefer manual installation:

```bash
# Install Python dependencies
pip install streamlit psycopg2-binary pandas plotly sqlalchemy

# Run the application
streamlit run app.py --server.port 5000
