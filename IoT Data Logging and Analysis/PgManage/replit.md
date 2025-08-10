# Overview

A comprehensive cross-platform PostgreSQL database management web application built with Streamlit and Python. The application provides a user-friendly interface for database administration, featuring dashboard analytics, database object exploration, DCL operations, query execution, and real-time monitoring capabilities. It serves as a complete database management solution with automated setup and interactive web-based interface.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web framework for rapid development of data applications
- **Layout**: Multi-page application with sidebar navigation and tabbed interfaces
- **Visualization**: Plotly integration for interactive charts and graphs
- **Styling**: Custom CSS with responsive design and metric cards
- **State Management**: Streamlit session state for maintaining connection and user preferences

## Backend Architecture
- **Database Layer**: PostgreSQL connection management through psycopg2
- **Connection Pooling**: Single connection instance stored in session state
- **Query Organization**: Centralized SQL queries in dedicated modules
- **Page Structure**: Modular page components with separation of concerns
- **Error Handling**: Comprehensive exception handling with user-friendly messages

## Core Components
- **Database Connection Manager**: Handles PostgreSQL connections, testing, and database selection
- **Query Executor**: Interactive SQL editor with syntax highlighting and result visualization
- **Dashboard Analytics**: Real-time database metrics, performance monitoring, and visual statistics
- **Object Browser**: Comprehensive exploration of tables, functions, procedures, triggers, and views
- **DCL Operations**: User and role management with privilege control
- **Event Management**: Trigger monitoring and event scheduling support

## Data Management
- **Query Results**: DataFrame-based result handling with CSV export capabilities
- **Caching**: Session-based caching for connection parameters and query history
- **Real-time Updates**: Auto-refresh functionality for dashboard metrics
- **Data Visualization**: Interactive charts for database statistics and performance metrics

## Security Architecture
- **Connection Security**: Secure credential handling with session isolation
- **Privilege Management**: Comprehensive DCL operations for user and role administration
- **Query Safety**: Parameterized queries to prevent SQL injection
- **Session Management**: Secure session state handling for multi-user scenarios

# External Dependencies

## Database Systems
- **PostgreSQL**: Primary database system (any compatible version)
- **psycopg2**: Python PostgreSQL adapter for database connectivity
- **pg_cron**: Optional extension for scheduled event support

## Python Framework
- **Streamlit**: Core web application framework for UI and interaction
- **Pandas**: Data manipulation and analysis for query results
- **Plotly**: Interactive visualization library for charts and graphs

## Development Tools
- **Cross-platform Setup**: Automated installation scripts for Windows and Linux
- **Package Management**: Requirements-based dependency management
- **Error Logging**: Built-in error handling and user feedback systems

## Optional Extensions
- **pg_cron**: PostgreSQL extension for job scheduling functionality
- **Additional PostgreSQL Extensions**: Support for various PostgreSQL extensions based on installation