# 🚀 Complete Setup and Usage Guide - Database Explorer

This guide will walk you through setting up and using the Database Explorer from start to finish.

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- [ ] Python 3.11 or higher installed
- [ ] MySQL Server 8.0+ running
- [ ] Git installed (for cloning)
- [ ] Terminal/Command prompt access
- [ ] Web browser (Chrome, Firefox, Safari, or Edge)

## 🔧 Step 1: System Setup

### 1.1 Check Python Installation
```bash
python --version
# Should show Python 3.11.x or higher
```

If Python is not installed:
- **Windows**: Download from [python.org](https://python.org)
- **macOS**: Use Homebrew: `brew install python@3.11`
- **Linux**: Use package manager: `sudo apt install python3.11`

### 1.2 Verify MySQL Installation
```bash
mysql --version
# Should show MySQL ver 8.0.x or higher
```

If MySQL is not installed:
- **Windows**: Download MySQL Installer from [mysql.com](https://dev.mysql.com/downloads/installer/)
- **macOS**: Use Homebrew: `brew install mysql`
- **Linux**: `sudo apt install mysql-server`

## 🗄️ Step 2: Database Setup

### 2.1 Start MySQL Service
```bash
# Windows (as Administrator)
net start mysql

# macOS/Linux
sudo systemctl start mysql
# OR
sudo service mysql start
```

### 2.2 Connect to MySQL and Create Database
```bash
mysql -u root -p
```

In MySQL console:
```sql
-- Create the database
CREATE DATABASE customersdb;

-- Use the database
USE customersdb;

-- Create all tables (copy from your schema)
CREATE TABLE `category` (
  `category_id` int NOT NULL AUTO_INCREMENT,
  `category_name` varchar(50) NOT NULL,
  `description` varchar(100) NOT NULL,
  `updated_on` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `category_name` (`category_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `customers` (
  `customer_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `gender` enum('male','female','other','prefer not to say') NOT NULL,
  `age` int DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `ph_num` varchar(20) NOT NULL,
  `address1` varchar(100) NOT NULL,
  `city` varchar(50) NOT NULL,
  `state` varchar(50) NOT NULL,
  `postal_code` varchar(10) NOT NULL,
  `country` varchar(50) NOT NULL,
  `registration_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`customer_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Continue with all other tables from your schema...
-- (Copy the complete CREATE TABLE statements for all 11 tables)

-- Exit MySQL
EXIT;
```

### 2.3 Verify Database Creation
```bash
mysql -u root -p -e "SHOW DATABASES;"
mysql -u root -p customersdb -e "SHOW TABLES;"
```

## 📁 Step 3: Project Setup

### 3.1 Download the Project
If you have the project files:
```bash
# Navigate to your desired directory
cd /path/to/your/projects

# If cloning from GitHub
git clone https://github.com/yourusername/database-explorer.git
cd database-explorer

# OR if you have the files locally, create directory
mkdir database-explorer
cd database-explorer
# Copy all project files here
```

### 3.2 Install Python Dependencies
```bash
# Install required packages
pip install streamlit>=1.47.1
pip install pandas>=2.3.1
pip install plotly>=6.2.0
pip install mysql-connector-python>=9.4.0
pip install networkx>=3.5
pip install openpyxl>=3.1.5
pip install faker>=20.0.0

# OR if you have requirements.txt
pip install -r requirements.txt
```

### 3.3 Configure Database Connection
Create a `.env` file (optional) or modify the database.py file:

**Option A: Environment Variables (.env file)**
```bash
# Create .env file
echo "DB_HOST=localhost" > .env
echo "DB_PORT=3306" >> .env
echo "DB_NAME=customersdb" >> .env
echo "DB_USER=root" >> .env
echo "DB_PASSWORD=password" >> .env
```

**Option B: Direct Configuration**
Edit `database.py` and update the password:
```python
'password': os.getenv('DB_PASSWORD', 'your_actual_password'),
```

## 🎲 Step 4: Generate Sample Data (Optional but Recommended)

### 4.1 Run the Data Generator
```bash
python data_generator.py
```

This will create:
- 1,500 customers
- 2,000 orders
- 3,000 order items
- 500 products
- 100 employees
- And more (10,000+ total records)

### 4.2 Verify Data Generation
```bash
mysql -u root -p customersdb -e "SELECT COUNT(*) FROM customers;"
mysql -u root -p customersdb -e "SELECT COUNT(*) FROM orders;"
mysql -u root -p customersdb -e "SELECT COUNT(*) FROM products;"
```

## 🚀 Step 5: Launch the Application

### 5.1 Start the Streamlit Server
```bash
streamlit run app.py --server.port 5000
```

You should see:
```
You can now view your Streamlit app in your browser.
URL: http://0.0.0.0:5000
```

### 5.2 Access the Web Interface
Open your web browser and navigate to:
```
http://localhost:5000
```

## 📊 Step 6: Using the Application

### 6.1 Main Dashboard
When you first load the app:
1. **Connection Status**: Check if "Connected to MySQL database successfully!" appears
2. **Overview Metrics**: View total tables, records, customers, and products
3. **Table Overview**: See all your database tables with record counts
4. **Quick Insights**: Interactive charts showing data distribution

### 6.2 Browse Tables (Tables Page)
1. Click "Tables" in the sidebar
2. Select a table from the dropdown
3. **Search**: Use the search box to find specific records
4. **Filter**: Choose specific columns to search in
5. **Pagination**: Navigate through large datasets
6. **View Structure**: Expand "Table Structure" to see column details

### 6.3 Analytics Dashboard (Analytics Page)
1. Click "Analytics" in the sidebar
2. Select a table to analyze
3. Choose visualization type:
   - **Overview Dashboard**: Table-specific insights
   - **Distribution Analysis**: Histograms and statistical analysis
   - **Correlation Analysis**: Relationship between numeric columns
   - **Time Series Analysis**: Trends over time
   - **Categorical Analysis**: Category distributions
   - **Custom Charts**: Build your own visualizations

### 6.4 Explore Relationships (Relationships Page)
1. Click "Relationships" in the sidebar
2. **Network Diagram**: Interactive visualization of table connections
3. **Relationship Details**: Table showing all foreign key relationships
4. **Table-Specific**: Select individual tables to see their connections
5. **Integrity Checks**: Run data validation checks

### 6.5 Export Data (Export Page)
1. Click "Export" in the sidebar
2. **Select Table**: Choose which table to export
3. **Choose Format**: CSV, Excel, or JSON
4. **Column Selection**: Pick specific columns
5. **Apply Filters**: Filter data before export
6. **Download**: Generate and download your file

## 🔧 Step 7: Advanced Usage

### 7.1 Custom Database Queries
For advanced users, you can modify the database.py file to add custom queries:
```python
def custom_analysis_query(self):
    query = """
    SELECT c.country, COUNT(*) as customer_count, AVG(o.total_amount) as avg_order
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.country
    ORDER BY customer_count DESC
    """
    return self.execute_query(query)
```

### 7.2 Adding New Visualizations
Create custom charts in the Analytics page by:
1. Going to "Custom Charts"
2. Selecting chart type
3. Choosing X and Y axes
4. Customizing colors and labels

### 7.3 Exporting Large Datasets
For large exports:
1. Use pagination and export in chunks
2. Apply filters to reduce data size
3. Use Excel format for multiple tables
4. Consider CSV for fastest processing

## 🚨 Troubleshooting

### Common Issues and Solutions

**❌ Database Connection Failed**
```bash
# Check MySQL is running
sudo systemctl status mysql

# Test connection manually
mysql -u root -p customersdb

# Verify credentials in database.py
```

**❌ "No module named 'streamlit'"**
```bash
# Install missing packages
pip install streamlit pandas plotly mysql-connector-python

# Check Python environment
which python
pip list
```

**❌ "Table 'customersdb.customers' doesn't exist"**
```bash
# Recreate database tables
mysql -u root -p customersdb < your_schema.sql

# OR run the CREATE TABLE statements manually
```

**❌ Performance Issues**
- Reduce page sizes in table browser
- Apply filters before loading large datasets
- Clear browser cache
- Restart Streamlit application

**❌ Empty Tables**
```bash
# Run data generator
python data_generator.py

# Check if data exists
mysql -u root -p customersdb -e "SELECT COUNT(*) FROM customers;"
```

## 🔄 Step 8: Regular Usage Workflow

### Daily Usage Pattern:
1. **Start**: `streamlit run app.py --server.port 5000`
2. **Browse**: Use Tables page to explore your data
3. **Analyze**: Create visualizations in Analytics
4. **Export**: Download reports as needed
5. **Monitor**: Check relationships and data integrity

### For New Data:
1. Add new records to your MySQL database
2. Refresh the Streamlit app (F5 in browser)
3. View updated metrics and charts
4. Export updated reports

### For Schema Changes:
1. Update MySQL table structures
2. Restart Streamlit application
3. Verify new columns appear in the interface
4. Update custom queries if needed

## 📈 Step 9: Extending the Application

### Adding New Features:
1. Create new page files in `pages/` directory
2. Add database methods in `database.py`
3. Create utility functions in `utils.py`
4. Test thoroughly before deployment

### Customizing Appearance:
1. Modify `.streamlit/config.toml` for themes
2. Update CSS in Streamlit components
3. Change color schemes in Plotly charts

## 💾 Step 10: Backup and Maintenance

### Regular Backups:
```bash
# Backup database
mysqldump -u root -p customersdb > backup_$(date +%Y%m%d).sql

# Restore database
mysql -u root -p customersdb < backup_20241127.sql
```

### Application Updates:
1. Keep dependencies updated
2. Monitor for Streamlit updates
3. Test with new MySQL versions
4. Document any configuration changes

## 🎉 Congratulations!

You now have a fully functional database visualization tool! The application provides:
- Real-time database exploration
- Interactive data visualization
- Comprehensive export capabilities
- Relationship mapping and analysis

For additional help, refer to the README.md file or check the troubleshooting section above.

---

**Need Help?** 
- Check the logs in your terminal
- Verify database connections
- Ensure all dependencies are installed
- Review the error messages carefully