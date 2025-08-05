# MySQL Database Manager

## Overview

This is a Streamlit-based web application that provides a comprehensive interface for managing MySQL databases. The application allows users to connect to MySQL servers, browse database objects (tables, views, procedures, functions, triggers), execute custom SQL queries, visualize data, and export results in multiple formats.

## User Preferences

Preferred communication style: Simple, everyday language.

**UI Preferences (Updated July 27, 2025):**
- Replace dropdowns with scrollable button lists for table/procedure selection
- Use button-based navigation instead of radio buttons
- Hide database connection form after first successful connection
- Add colorful visual dashboard with gradient backgrounds
- Include record counts and statistics in dashboard
- Form-based parameter input for stored procedures with proper data types
- Show procedure call syntax examples for user guidance

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework for rapid development of data applications
- **Layout**: Wide layout with expandable sidebar for navigation and connection management
- **State Management**: Uses Streamlit's session state to maintain connection status and database context
- **User Interface**: Clean, intuitive interface with forms, buttons, and interactive components

### Backend Architecture
- **Database Connectivity**: SQLAlchemy ORM with PyMySQL driver for MySQL connections
- **Modular Design**: Separated into distinct modules for different functionalities:
  - `database_manager.py`: Core database operations and connection management
  - `query_executor.py`: SQL query execution with safety checks and timing
  - `data_visualizer.py`: Chart creation using Plotly for data visualization
  - `export_utils.py`: Data export functionality in multiple formats
- **Error Handling**: Comprehensive exception handling with logging throughout the application

## Key Components

### DatabaseManager Class
- **Purpose**: Handles MySQL connections and database operations
- **Features**: 
  - Dynamic database discovery and selection
  - Connection pooling with pre-ping for reliability
  - Support for multiple database object types (tables, views, procedures, functions, triggers)
  - Schema inspection capabilities
- **Connection String Format**: `mysql+pymysql://user:password@host:port/database_name`

### QueryExecutor Class
- **Purpose**: Safe execution of custom SQL queries
- **Features**:
  - Query validation and timing
  - Basic safety checks for dangerous operations (DROP, DELETE, etc.)
  - Result formatting as pandas DataFrames
  - Execution time tracking

### DataVisualizer Class
- **Purpose**: Creates interactive charts from query results
- **Supported Charts**: Bar charts, line charts, scatter plots, histograms, box plots
- **Technology**: Plotly Express and Graph Objects for interactive visualizations
- **Data Handling**: Automatic data type detection and aggregation

### ExportUtils Class
- **Purpose**: Export data in multiple formats
- **Supported Formats**: CSV, JSON, Excel
- **Features**: Configurable export options and error handling

## Data Flow

1. **Connection**: User provides MySQL credentials through sidebar form
2. **Database Selection**: Application discovers available databases and allows selection
3. **Object Browsing**: User can browse tables, views, procedures, functions, and triggers
4. **Data Interaction**: Users can view table data with pagination and search functionality
5. **Query Execution**: Custom SQL queries can be executed with results displayed in tabular format
6. **Visualization**: Numeric data can be visualized using various chart types
7. **Export**: Results can be exported in CSV, JSON, or Excel formats

## External Dependencies

### Core Dependencies
- **streamlit**: Web application framework (>=1.28.0)
- **pandas**: Data manipulation and analysis (>=1.5.0)
- **sqlalchemy**: SQL toolkit and ORM (>=2.0.0)
- **pymysql**: Pure Python MySQL client (>=1.1.0)
- **mysql-connector-python**: Official MySQL driver (>=8.1.0)

### Visualization and Export
- **plotly**: Interactive plotting library (>=5.15.0)
- **openpyxl**: Excel file handling (>=3.1.0)
- **xlsxwriter**: Excel file creation (>=3.1.0)

### Database Requirements
- **MySQL Server**: Version 5.7 or higher
- **Default Configuration**: Expects MySQL running on localhost:3306
- **Required Databases**: Excludes system databases (information_schema, performance_schema, mysql, sys)

## Deployment Strategy

### Local Development
- **Platform**: Designed for Windows 10/11 environments
- **Python Version**: Requires Python 3.7 or higher
- **MySQL Setup**: Requires local MySQL installation and configuration

### Application Structure
- **Entry Point**: `app.py` serves as the main Streamlit application
- **Modular Architecture**: Functionality split across specialized modules
- **Configuration**: Connection parameters configurable through UI
- **Error Recovery**: Built-in connection retry and error handling mechanisms

### Security Considerations
- **Query Safety**: Basic protection against dangerous SQL operations
- **Connection Management**: Secure password handling through Streamlit's input masking
- **Logging**: Comprehensive logging for debugging and monitoring
- **Connection Pooling**: Proper connection lifecycle management to prevent resource leaks

The application follows a traditional client-server architecture where the Streamlit frontend communicates directly with the MySQL database through SQLAlchemy, providing a user-friendly interface for database management tasks without requiring deep SQL knowledge from end users.