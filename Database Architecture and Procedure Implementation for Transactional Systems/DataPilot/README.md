# 📊 Database Explorer - MySQL Visualization Tool

A comprehensive Streamlit web application for exploring, visualizing, and managing MySQL databases with interactive charts, data browsing, and export capabilities.

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.47+-red.svg)
![MySQL](https://img.shields.io/badge/mysql-8.0+-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

### 📈 Dashboard Overview
- Real-time database connection status
- Total tables, records, and key metrics
- Interactive overview charts
- Quick navigation to all features

### 📋 Table Browser
- Browse all database tables with pagination
- Advanced search and filtering
- Column metadata and structure analysis
- Data quality metrics and statistics
- Real-time record counting

### 📊 Analytics Dashboard
- Interactive charts and visualizations
- Distribution analysis for numeric data
- Correlation matrices and heatmaps
- Time series analysis
- Categorical data exploration
- Custom chart builder

### 🔗 Relationship Visualization
- Interactive network diagrams of table relationships
- Foreign key relationship mapping
- Data integrity checks
- Relationship analysis and statistics

### 💾 Data Export
- Multiple export formats (CSV, Excel, JSON)
- Bulk table export functionality
- Custom column selection
- Advanced filtering options
- Pre-configured export templates

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MySQL Server 8.0+
- Required Python packages (see Dependencies)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/database-explorer.git
cd database-explorer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
# OR if using the pyproject.toml
pip install -e .
```

3. **Configure database connection**
Set environment variables or modify `database.py`:
```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=customersdb
export DB_USER=root
export DB_PASSWORD=password
```

4. **Run the application**
```bash
streamlit run app.py --server.port 5000
```

5. **Access the web interface**
Open your browser and navigate to `http://localhost:5000`

## 🗄️ Database Schema

The application works with the following MySQL database structure:

### Core Tables
- **`customers`** - Customer information with demographics
- **`employees`** - Employee data with hierarchical relationships
- **`category`** - Product categories with descriptions
- **`products`** - Product catalog with category relationships
- **`orders`** - Order transactions and totals
- **`orderitems`** - Individual order line items
- **`inventory`** - Product inventory levels
- **`price`** - Product pricing information
- **`shipping`** - Order shipping and delivery tracking
- **`log`** - System activity and change logs

### 🔗 Relationships
- Products → Categories (Foreign Key)
- Orders → Customers (Foreign Key)
- Order Items → Products & Customers (Foreign Keys)
- Employees → Employees (Self-referencing for managers)
- Inventory & Pricing → Products (Foreign Keys)

## 📊 Sample Data Generation

Generate over 10,000 sample records for testing:

```bash
python data_generator.py
```

This will create:
- 1,500 Customers
- 2,000 Orders
- 3,000 Order Items
- 500 Products
- 100 Employees
- And more...

## 🏗️ Project Structure

```
database-explorer/
├── app.py                 # Main Streamlit application
├── database.py           # Database connection and operations
├── utils.py              # Utility functions and helpers
├── data_generator.py     # Sample data generation script
├── pages/                # Streamlit pages
│   ├── 1_Tables.py      # Table browser interface
│   ├── 2_Analytics.py   # Analytics dashboard
│   ├── 3_Relationships.py # Relationship visualization
│   └── 4_Export.py      # Data export functionality
├── .streamlit/          # Streamlit configuration
│   └── config.toml      # Server and theme settings
├── pyproject.toml       # Python dependencies
└── README.md           # This file
```

## 🔧 Configuration

### Database Configuration
The application supports configuration via environment variables:

```bash
# Database connection
DB_HOST=localhost          # MySQL host
DB_PORT=3306              # MySQL port
DB_NAME=customersdb       # Database name
DB_USER=root              # MySQL username
DB_PASSWORD=password      # MySQL password
```

### Streamlit Configuration
Server settings are configured in `.streamlit/config.toml`:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
base = "light"
```

## 📦 Dependencies

### Core Dependencies
- **streamlit** `>=1.47.1` - Web application framework
- **pandas** `>=2.3.1` - Data manipulation and analysis
- **plotly** `>=6.2.0` - Interactive visualization library
- **mysql-connector-python** `>=9.4.0` - MySQL database connectivity

### Additional Dependencies
- **networkx** `>=3.5` - Graph analysis for relationship mapping
- **openpyxl** `>=3.1.5` - Excel file export support
- **faker** `>=20.0.0` - Sample data generation (optional)

## 🎯 Usage Examples

### Analyzing Customer Data
1. Navigate to the **Tables** page
2. Select the `customers` table
3. Use search filters to find specific customers
4. View summary statistics and data quality metrics

### Creating Visualizations
1. Go to the **Analytics** page
2. Select your table and chart type
3. Choose columns for X and Y axes
4. Customize the visualization settings
5. Export charts as images if needed

### Exploring Relationships
1. Visit the **Relationships** page
2. View the interactive network diagram
3. Click on tables to see detailed connections
4. Run integrity checks to validate data quality

### Exporting Data
1. Access the **Export** page
2. Select tables and columns to export
3. Choose your preferred format (CSV, Excel, JSON)
4. Apply filters and download your data

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py --server.port 5000
```

### Production Deployment
For production deployment, consider:
- Using environment variables for sensitive configuration
- Setting up SSL/TLS certificates
- Configuring proper database connection pooling
- Setting up monitoring and logging

### Docker Deployment (Optional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 5000

CMD ["streamlit", "run", "app.py", "--server.port", "5000"]
```

## 🛠️ Development

### Setting up Development Environment
1. Clone the repository
2. Create a virtual environment
3. Install dependencies in development mode
4. Set up your MySQL database
5. Run the data generator for sample data

### Code Structure
- **app.py** - Main dashboard and entry point
- **database.py** - Database operations and connection management
- **utils.py** - Shared utility functions and chart helpers
- **pages/** - Individual Streamlit pages for different features

### Adding New Features
1. Create new page files in the `pages/` directory
2. Add database methods in `database.py` if needed
3. Create utility functions in `utils.py` for reusable code
4. Update navigation and documentation

## 🔍 Troubleshooting

### Common Issues

**Database Connection Failed**
- Verify MySQL server is running
- Check connection credentials
- Ensure database exists
- Verify network connectivity

**Performance Issues**
- Limit data loading with pagination
- Use data caching where appropriate
- Optimize database queries
- Consider adding database indexes

**Memory Issues**
- Reduce data loading limits
- Clear browser cache
- Restart the Streamlit application

## 📈 Performance Optimization

- **Data Caching**: Streamlit's `@st.cache_data` decorator caches query results
- **Connection Pooling**: Database connections are managed efficiently
- **Pagination**: Large datasets are loaded in chunks
- **Lazy Loading**: Data is loaded only when needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the web framework
- Visualizations powered by [Plotly](https://plotly.com/)
- Data processing with [Pandas](https://pandas.pydata.org/)
- Database connectivity via [MySQL Connector](https://dev.mysql.com/doc/connector-python/en/)

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

---

**Made with ❤️ for database exploration and visualization**