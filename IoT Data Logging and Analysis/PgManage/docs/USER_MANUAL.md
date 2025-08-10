# PostgreSQL Database Manager - User Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Tables Management](#tables-management)
4. [Functions & Procedures](#functions--procedures)
5. [Triggers Management](#triggers-management)
6. [DCL Operations](#dcl-operations)
7. [Query Executor](#query-executor)
8. [Best Practices](#best-practices)

## Getting Started

### Initial Setup

1. **Launch the Application**
   - Windows: Run `run.bat`
   - Linux: Run `./run.sh`
   - The application opens at `http://localhost:5000`

2. **Database Connection**
   - Use the sidebar connection form
   - Enter your PostgreSQL connection details
   - Click "Connect" to establish connection
   - Select your target database from the dropdown

### Default Connection Settings
- **Host**: localhost
- **Port**: 5432  
- **Username**: postgres
- **Password**: password

## Dashboard Overview

The dashboard provides a comprehensive overview of your PostgreSQL database:

### Overview Metrics
- **Tables**: Total number of tables in the database
- **Views**: Number of views (regular and materialized)
- **Functions**: Count of stored functions
- **Procedures**: Count of stored procedures
- **Triggers**: Number of triggers (table and event triggers)
- **Indexes**: Total index count
- **Database Size**: Current database storage usage
- **Active Connections**: Number of active database connections

### Database Statistics
- **Transaction Statistics**: Commits vs rollbacks with visual charts
- **Cache Performance**: Cache hit ratio and disk read statistics
- **Tuple Operations**: Insert, update, delete operations count

### Table Analytics
- **Row Count Visualization**: Bar charts showing largest tables by row count
- **Table Information**: Detailed table listing with sizes and metadata
- **Performance Metrics**: Table access patterns and statistics

### Auto-Refresh Feature
Enable the auto-refresh checkbox to automatically update dashboard metrics every 30 seconds.

## Tables Management

### All Tables View

**Features:**
- Complete table listing with schema, name, type, and row counts
- Search functionality to filter tables by name or schema
- Real-time row count calculation
- Size information for each table
- Summary statistics (total tables, rows, columns, schemas)

### Table Details

**Available Information:**
- **Columns**: Data types, constraints, nullable status, default values
- **Indexes**: Index definitions and types
- **Constraints**: Primary keys, foreign keys, check constraints
- **Statistics**: Table size, row counts, activity metrics, maintenance info

### Table Data Viewer

**Features:**
- Paginated data viewing with customizable page size
- Offset controls for navigation through large datasets
- Real-time data refresh
- Full table data export capabilities

**Usage Tips:**
- Use smaller page sizes (10-100 rows) for large tables
- Utilize the offset feature to navigate through data efficiently
- Refresh data regularly when viewing frequently updated tables

## Functions & Procedures

### Function Management

**Viewing Functions:**
- Browse all functions and procedures by schema
- Filter by function type (FUNCTION vs PROCEDURE)
- Search by name or schema
- View function signatures and return types

**Function Details:**
- Parameter information with data types and modes
- Complete source code viewing
- Return type information
- Schema and ownership details

### Function Execution

**Steps to Execute:**
1. Select function from the dropdown
2. Enter parameter values in the input form
3. Click "Execute Function"
4. View results in the output panel

**Parameter Types:**
- **IN**: Input parameters (required)
- **OUT**: Output parameters (automatically handled)
- **INOUT**: Input/Output parameters

**Execution Tips:**
- Leave parameters empty for NULL values
- String parameters are automatically quoted
- Review the generated SQL before execution

## Triggers Management

### Table Triggers

**Information Displayed:**
- Trigger name and associated table
- Event type (INSERT, UPDATE, DELETE)
- Timing (BEFORE, AFTER)
- Trigger function details

**Filtering Options:**
- Filter by event type
- Filter by timing (BEFORE/AFTER)
- Search by trigger name or table

### Event Triggers

**Features:**
- Database-wide event trigger monitoring
- Event type distribution charts
- Trigger status and ownership information
- Function association details

### Trigger Details

**Available Information:**
- Complete trigger definition
- Associated trigger function source code
- Trigger metadata and status
- Enable/disable status

## DCL Operations

### User & Role Management

**User Information:**
- Username and role details
- Privilege flags (superuser, create role, create DB, login, replication)
- Account validity periods
- Password status

**Creating Users/Roles:**
1. Fill in the user creation form
2. Set appropriate privileges
3. Optionally set password and expiration
4. Click "Create User/Role"

### Privilege Management

**Grant Privileges:**
- Table-level privileges (SELECT, INSERT, UPDATE, DELETE, etc.)
- Schema-level privileges (USAGE, CREATE)
- Grant option support for privilege delegation

**Revoke Privileges:**
- Remove specific privileges from users
- CASCADE option for dependent object privilege removal
- Schema and table privilege revocation

### Security Overview

**Security Monitoring:**
- Detection of users without passwords
- Identification of expired accounts
- Superuser account auditing
- Privilege distribution analysis

**Security Recommendations:**
- Regular privilege audits
- Strong password enforcement
- Principle of least privilege
- SSL/TLS connection usage

## Query Executor

### SQL Editor

**Features:**
- Syntax highlighting for SQL
- Query type selection with templates
- Execution time measurement
- Result limiting for large datasets

**Query Types with Templates:**
- **SELECT**: Data retrieval queries
- **INSERT**: Data insertion statements
- **UPDATE**: Data modification queries
- **DELETE**: Data removal statements
- **CREATE**: Object creation DDL
- **ALTER**: Object modification DDL
- **DROP**: Object removal DDL
- **GRANT/REVOKE**: Privilege management

### Query Execution

**Execution Options:**
- Auto-commit for automatic transaction handling
- Execution time display
- Result set limiting (default: 1000 rows)
- EXPLAIN query analysis

**Result Handling:**
- Tabular result display
- CSV export functionality
- Query history tracking
- Error message display with suggestions

### Query History

**Features:**
- Last 50 queries tracked
- Success/failure status
- Execution time logging
- Query re-execution capability
- History filtering by status

### Quick Reference

**Built-in Documentation:**
- SELECT query examples
- DDL command templates
- DCL command syntax
- PostgreSQL-specific features
- Common function reference

## Best Practices

### Security Best Practices

1. **User Management:**
   - Create specific users for different applications
   - Avoid using superuser accounts for routine operations
   - Regularly review and audit user privileges
   - Set expiration dates for temporary accounts

2. **Privilege Management:**
   - Apply principle of least privilege
   - Grant only necessary permissions
   - Use roles for group privilege management
   - Regularly audit granted privileges

3. **Connection Security:**
   - Use SSL/TLS connections in production
   - Avoid storing passwords in configuration files
   - Use environment variables for sensitive data
   - Implement connection pooling for applications

### Performance Best Practices

1. **Query Optimization:**
   - Use EXPLAIN to analyze query performance
   - Add appropriate indexes for frequently queried columns
   - Avoid SELECT * in production queries
   - Use LIMIT for large result sets

2. **Database Maintenance:**
   - Monitor table statistics and dead tuples
   - Run VACUUM and ANALYZE regularly
   - Monitor index usage and remove unused indexes
   - Keep statistics up to date

3. **Monitoring:**
   - Use the dashboard for regular database health checks
   - Monitor active connections and query performance
   - Track database size growth
   - Review cache hit ratios regularly

### Data Management Best Practices

1. **Table Design:**
   - Use appropriate data types
   - Implement proper constraints
   - Design efficient indexes
   - Consider partitioning for large tables

2. **Backup and Recovery:**
   - Implement regular backup schedules
   - Test backup restoration procedures
   - Monitor backup success and failures
   - Consider point-in-time recovery requirements

3. **Application Integration:**
   - Use connection pooling
   - Implement proper error handling
   - Use parameterized queries to prevent SQL injection
   - Monitor application query patterns

### Troubleshooting Tips

1. **Connection Issues:**
   - Verify PostgreSQL service status
   - Check firewall and network connectivity
   - Validate connection parameters
   - Review pg_hba.conf authentication settings

2. **Performance Issues:**
   - Use EXPLAIN ANALYZE for slow queries
   - Monitor system resources (CPU, memory, disk I/O)
   - Check for lock contention
   - Review database statistics

3. **Permission Issues:**
   - Verify user privileges for specific operations
   - Check role membership and inheritance
   - Review object ownership
   - Validate schema access permissions

---

For additional support, refer to the [Troubleshooting Guide](TROUBLESHOOTING.md) or PostgreSQL official documentation.
