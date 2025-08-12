# Overview

A comprehensive cross-platform PostgreSQL database management web application built with Streamlit and Python. The application provides a user-friendly interface for database administration, featuring dashboard analytics, database object exploration, DCL operations, query execution, and real-time monitoring capabilities. It serves as a complete database management solution with automated setup and interactive web-based interface.

# User Preferences

Preferred communication style: Simple, everyday language.

# Recent Changes (August 2025)

## Navigation and UI Improvements
- Fixed sidebar navigation structure to remove unwanted options above database connection form
- Cleaned up navigation menu to show only when properly connected
- Added ERD (Entity Relationship Diagram) page with interactive visualization

## DCL Operations Enhancements  
- Enhanced DCL operations with comprehensive SQL code generation and preview
- Added checkbox interface for all privilege types instead of multiselect dropdowns
- Implemented real-time SQL code preview for all DCL operations (CREATE ROLE, GRANT, REVOKE)
- Added revoke privileges functionality with CASCADE/RESTRICT options
- Added user/role deletion capabilities with confirmation prompts
- Enhanced privilege types to include Database, Schema, Table, Sequence, Function, and Type
- Added WITH GRANT OPTION support for privilege delegation
- Implemented comprehensive security overview with recommendations

## Tables Page Enhancements
- Added Column Statistics tab with detailed analysis for numeric and text columns
- Implemented descriptive statistics (min, max, avg, std deviation) for numeric columns  
- Added unique value counts and most common values analysis for text columns
- Enhanced table statistics with null percentage and uniqueness calculations
- Added comprehensive column type categorization and summary

## ERD Functionality
- Created interactive Entity Relationship Diagram visualization using Plotly
- Displays table relationships with foreign key connections
- Shows schema overview with table counts and column statistics
- Provides detailed relationship information with constraint rules
- Interactive table positioning and relationship mapping

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