# MySQL Database Manager

A comprehensive Streamlit-based web application for managing MySQL databases with an intuitive interface for viewing tables, executing queries, and visualizing data.

## 🚀 Features

### Database Management
- **Direct MySQL Connection**: Connect using exact connection string format `mysql+pymysql://root:password@localhost:3306/database_name`
- **Database Selection**: Dynamic dropdown to switch between available databases
- **Connection Management**: Secure connection handling with error recovery

### Database Objects Support
- **Tables**: Browse data with pagination, search, and schema inspection
- **Views**: View data and definitions
- **Stored Procedures**: Execute procedures and view definitions
- **Functions**: Inspect function definitions and code
- **Triggers**: View trigger definitions and associated tables

### Interactive Features
- **Custom SQL Execution**: Built-in query editor with syntax validation
- **Data Visualization**: Interactive charts using Plotly (bar, line, scatter, histogram, box plots)
- **Data Export**: Export to CSV, JSON, Excel formats
- **Real-time Search**: Search within table data
- **Pagination**: Handle large datasets efficiently

### Advanced Capabilities
- **Database Dashboard**: Overview with statistics and metrics
- **Table Schema Inspection**: Detailed column information and constraints
- **Query History**: Track executed queries
- **Data Type Optimization**: Automatic data type detection and conversion

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10/11
- **Python**: 3.7 or higher
- **MySQL**: 5.7 or higher running on localhost:3306

### Python Dependencies
- streamlit>=1.28.0
- pandas>=1.5.0
- plotly>=5.15.0
- sqlalchemy>=2.0.0
- pymysql>=1.1.0
- mysql-connector-python>=8.1.0
- openpyxl>=3.1.0
- xlsxwriter>=3.1.0

## 🛠️ Installation

### Method 1: Quick Setup (Recommended)

1. **Download the application files** to a directory on your computer

2. **Run the setup script**:
   ```cmd
   setup.bat
   ```
   This will automatically install all required Python dependencies.

3. **Start the application**:
   ```cmd
   run.bat
   ```

### Method 2: Manual Installation

1. **Install Python dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

2. **Start the application**:
   ```cmd
   streamlit run app.py --server.port 5000
   ```

## 🔧 Configuration

### MySQL Connection Setup

The application uses the following default connection parameters:
- **Host**: localhost (fixed)
- **Port**: 3306 (fixed)
- **Username**: root (configurable)
- **Password**: password (configurable)

**Connection String Format**: `mysql+pymysql://username:password@localhost:3306/database_name`

### Application Configuration

The application includes a `.streamlit/config.toml` file with optimized settings:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
base = "light"
