# Database Explorer - Streamlit MySQL Visualization Tool

## Overview

This is a Streamlit-based web application for exploring and visualizing MySQL databases. The application provides an interactive dashboard for browsing database tables, analyzing data with charts, exploring relationships between tables, and exporting data in various formats.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - A Python web framework for creating data applications
- **Multi-page Structure**: Uses Streamlit's native multi-page functionality with separate Python files in the `pages/` directory
- **Visualization**: Plotly Express and Plotly Graph Objects for interactive charts and graphs
- **Styling**: Built-in Streamlit components with wide layout and sidebar navigation

### Backend Architecture
- **Language**: Python
- **Database Layer**: Custom `DatabaseConnection` class wrapping MySQL Connector
- **Data Processing**: Pandas for data manipulation and analysis
- **Caching**: Streamlit's built-in caching decorators (`@st.cache_resource`, `@st.cache_data`) for performance optimization

### Database Architecture
- **Database**: MySQL (specifically targets a database named 'customersdb')
- **Connection Management**: Connection pooling handled through environment variables
- **Schema**: Multi-table relational database with tables including customers, employees, categories, and inventory

## Key Components

### Core Application (`app.py`)
- Main dashboard entry point
- Database connection initialization with caching
- Overview metrics and navigation setup
- Connection testing and error handling

### Database Layer (`database.py`)
- `DatabaseConnection` class for MySQL operations
- Environment-based configuration management
- Connection testing and management
- Methods for table operations (implied from usage patterns)

### Utility Functions (`utils.py`)
- Number formatting utilities for large numbers (K, M suffixes)
- Table metadata extraction and analysis
- Chart creation helpers for Plotly visualizations
- Data type identification and summary statistics

### Page Components
1. **Tables Page** (`pages/1_Tables.py`): Table browsing and detailed schema exploration
2. **Analytics Page** (`pages/2_Analytics.py`): Data visualization and statistical analysis
3. **Relationships Page** (`pages/3_Relationships.py`): Database relationship mapping and foreign key visualization
4. **Export Page** (`pages/4_Export.py`): Data export functionality in multiple formats

## Data Flow

1. **Initialization**: App starts by establishing cached database connection
2. **Table Discovery**: Application queries MySQL to discover available tables
3. **Data Loading**: Selected tables are loaded with performance limits (5000 records max)
4. **Processing**: Data is processed using Pandas for analysis and visualization
5. **Visualization**: Charts and metrics are generated using Plotly
6. **Export**: Data can be exported in CSV, Excel, or JSON formats

## External Dependencies

### Core Dependencies
- `streamlit`: Web application framework
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive visualization library
- `mysql-connector-python`: MySQL database connectivity
- `networkx`: Graph analysis for relationship mapping

### Environment Configuration
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 3306)
- `DB_NAME`: Database name (default: customersdb)
- `DB_USER`: Database username (default: root)
- `DB_PASSWORD`: Database password (default: empty)

## Deployment Strategy

### Local Development
- Streamlit development server with hot reloading
- Local MySQL server required
- Environment variables for database configuration

### Production Considerations
- Database connection pooling and error handling implemented
- Caching strategies for performance optimization
- Data loading limits to prevent memory issues
- Modular structure allows for easy scaling and maintenance

### Database Schema
The application expects a MySQL database with tables including:
- `customers`: Customer information with demographics and contact details
- `employees`: Employee data with hierarchical relationships (manager_id foreign key)
- `category`: Product/service categories with descriptions
- Additional inventory and transaction tables (referenced but not fully shown)

The schema uses standard MySQL features including:
- Auto-incrementing primary keys
- Foreign key constraints
- Enum types for controlled values
- Unique constraints on email fields
- Default timestamps and date functions