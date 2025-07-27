# Troubleshooting Guide - MySQL Database Manager

This guide covers common issues and their solutions when using the MySQL Database Manager application.

## 🔌 Connection Issues

### Issue: "Connection failed: (2003, "Can't connect to MySQL server on 'localhost' (10061)")"

**Cause**: MySQL server is not running or not accessible on localhost:3306

**Solutions**:
1. **Start MySQL Service**:
   ```cmd
   net start mysql
   # or
   net start mysql80  # for MySQL 8.0
   ```

2. **Check MySQL Service Status**:
   - Open Services (services.msc)
   - Look for MySQL service
   - Ensure it's running and set to "Automatic"

3. **Verify MySQL Port**:
   ```cmd
   netstat -an | findstr 3306
   ```
   Should show: `TCP 0.0.0.0:3306 0.0.0.0:0 LISTENING`

4. **Test Direct Connection**:
   ```cmd
   mysql -u root -p -h localhost -P 3306
   ```

### Issue: "Access denied for user 'root'@'localhost' (using password: YES)"

**Cause**: Incorrect username/password or user doesn't have privileges

**Solutions**:
1. **Reset MySQL Root Password**:
   ```cmd
   # Stop MySQL service
   net stop mysql
   
   # Start MySQL without authentication
   mysqld --skip-grant-tables --skip-networking
   
   # In another command prompt:
   mysql -u root
   
   # Reset password
   USE mysql;
   UPDATE user SET authentication_string = PASSWORD('password') WHERE User = 'root';
   FLUSH PRIVILEGES;
   exit;
   
   # Restart MySQL normally
   net start mysql
   ```

2. **Create New Database User**:
   ```sql
   CREATE USER 'dbmanager'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON *.* TO 'dbmanager'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Check User Privileges**:
   ```sql
   SHOW GRANTS FOR 'root'@'localhost';
   ```

### Issue: "Unknown database 'database_name'"

**Cause**: Database doesn't exist or user doesn't have access

**Solutions**:
1. **List Available Databases**:
   ```sql
   SHOW DATABASES;
   ```

2. **Create Database** (if needed):
   ```sql
   CREATE DATABASE your_database_name;
   ```

3. **Grant Access to Database**:
   ```sql
   GRANT ALL PRIVILEGES ON database_name.* TO 'username'@'localhost';
   ```

### Issue: "OperationalError: (2013, 'Lost connection to MySQL server during query')"

**Cause**: Query timeout or MySQL server issues

**Solutions**:
1. **Increase MySQL Timeout Settings**:
   ```sql
   SET SESSION wait_timeout = 600;
   SET SESSION interactive_timeout = 600;
   ```

2. **Check MySQL Configuration** (my.ini or my.cnf):
   ```ini
   [mysqld]
   wait_timeout = 600
   interactive_timeout = 600
   max_allowed_packet = 64M
   ```

3. **Restart Application**: Sometimes reconnection resolves the issue

## 🐍 Python and Package Issues

### Issue: "Python is not recognized as an internal or external command"

**Cause**: Python not installed or not in system PATH

**Solutions**:
1. **Install Python**:
   - Download from https://python.org/downloads/
   - **Important**: Check "Add Python to PATH" during installation

2. **Add Python to PATH Manually**:
   - Find Python installation directory (usually `C:\Python39\` or `C:\Users\YourName\AppData\Local\Programs\Python\Python39\`)
   - Add to System PATH in Environment Variables

3. **Verify Installation**:
   ```cmd
   python --version
   pip --version
   ```

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Cause**: Required Python packages not installed

**Solutions**:
1. **Run Setup Script**:
   ```cmd
   setup.bat
   ```

2. **Manual Installation**:
   ```cmd
   pip install streamlit pandas plotly sqlalchemy pymysql mysql-connector-python openpyxl xlsxwriter
   ```

3. **Check Python Environment**:
   ```cmd
   pip list
   ```

4. **Upgrade pip**:
   ```cmd
   python -m pip install --upgrade pip
   ```

### Issue: "ERROR: Could not install packages due to an EnvironmentError"

**Cause**: Permission issues or conflicting packages

**Solutions**:
1. **Run as Administrator**:
   - Right-click Command Prompt
   - Select "Run as administrator"
   - Run setup.bat again

2. **Use User Installation**:
   ```cmd
   pip install --user streamlit pandas plotly sqlalchemy pymysql
   ```

3. **Clear pip Cache**:
   ```cmd
   pip cache purge
   ```

## 🌐 Application Issues

### Issue: "Address already in use" or Port 5000 Error

**Cause**: Another application is using port 5000

**Solutions**:
1. **Find Process Using Port**:
   ```cmd
   netstat -ano | findstr :5000
   ```

2. **Kill Process** (if safe to do so):
   ```cmd
   taskkill /PID <process_id> /F
   ```

3. **Use Different Port**:
   Edit run.bat and change:
   ```cmd
   streamlit run app.py --server.port 5001
   ```

### Issue: Application starts but shows blank page

**Cause**: Browser compatibility or caching issues

**Solutions**:
1. **Clear Browser Cache**: Ctrl+F5 or clear browser cache

2. **Try Different Browser**: Chrome, Firefox, or Edge

3. **Check URL**: Ensure you're accessing http://localhost:5000

4. **Disable Extensions**: Try browser in incognito/private mode

5. **Check Firewall**: Ensure Windows Firewall allows the connection

### Issue: "Config.toml not found" or Configuration Errors

**Cause**: Missing or corrupted configuration file

**Solutions**:
1. **Recreate .streamlit Directory**:
   ```cmd
   mkdir .streamlit
   ```

2. **Create config.toml**:
   ```toml
   [server]
   headless = true
   address = "0.0.0.0"
   port = 5000
   
   [theme]
   base = "light"
   ```

## 📊 Data and Performance Issues

### Issue: "Table data not loading" or Very Slow Performance

**Cause**: Large datasets or inefficient queries

**Solutions**:
1. **Reduce Page Size**:
   - Use smaller "Rows per page" setting (10-25)
   - Implement search filters

2. **Add Database Indexes**:
   ```sql
   CREATE INDEX idx_column_name ON table_name(column_name);
   ```

3. **Optimize MySQL Configuration**:
   ```ini
   [mysqld]
   innodb_buffer_pool_size = 256M
   query_cache_size = 64M
   ```

### Issue: "Export fails for large datasets"

**Cause**: Memory limitations or timeout issues

**Solutions**:
1. **Limit Export Rows**:
   - Set row limit in export options
   - Export in smaller batches

2. **Use CSV Format**: Most memory-efficient for large datasets

3. **Increase System Memory**: Close other applications

### Issue: "Visualization not displaying" or Chart Errors

**Cause**: Incompatible data types or missing data

**Solutions**:
1. **Check Data Types**:
   - Ensure numeric columns for numeric charts
   - Remove null values if causing issues

2. **Update Plotly**:
   ```cmd
   pip install --upgrade plotly
   ```

3. **Try Different Chart Types**: Some charts work better with certain data

## 🔧 MySQL Server Issues

### Issue: "MySQL service won't start"

**Cause**: Configuration errors or corrupted files

**Solutions**:
1. **Check MySQL Error Log**:
   - Usually in `C:\ProgramData\MySQL\MySQL Server 8.0\Data\`
   - Look for .err files

2. **Repair MySQL Installation**:
   - Use MySQL Installer to repair
   - Or reinstall MySQL

3. **Check Port Conflicts**:
   ```cmd
   netstat -an | findstr 3306
   ```

4. **Run MySQL Configuration Wizard**:
   ```cmd
   mysql_secure_installation
   ```

### Issue: "Too many connections" Error

**Cause**: MySQL connection limit reached

**Solutions**:
1. **Check Current Connections**:
   ```sql
   SHOW PROCESSLIST;
   SHOW STATUS LIKE 'Threads_connected';
   ```

2. **Increase Connection Limit**:
   ```sql
   SET GLOBAL max_connections = 200;
   ```

3. **Kill Sleeping Connections**:
   ```sql
   SELECT CONCAT('KILL ', id, ';') FROM information_schema.processlist WHERE command = 'Sleep';
   ```

## 🛡️ Security and Permissions

### Issue: "Access denied" for Database Operations

**Cause**: Insufficient user privileges

**Solutions**:
1. **Grant Necessary Privileges**:
   ```sql
   -- For read-only access
   GRANT SELECT ON database_name.* TO 'username'@'localhost';
   
   -- For full access
   GRANT ALL PRIVILEGES ON database_name.* TO 'username'@'localhost';
   
   -- For specific operations
   GRANT SELECT, INSERT, UPDATE, DELETE ON database_name.* TO 'username'@'localhost';
   
   FLUSH PRIVILEGES;
   