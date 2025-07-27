#!/usr/bin/env python3
"""
Quick Start Script for Database Explorer
Automates the setup and launch process
"""

import os
import sys
import subprocess
import mysql.connector
from pathlib import Path

def print_header():
    """Print welcome header"""
    print("=" * 60)
    print("🚀 DATABASE EXPLORER - QUICK START")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11+ required. Current version:", f"{version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True

def check_mysql_connection():
    """Test MySQL database connection"""
    print("\n🔍 Testing MySQL connection...")
    
    # Get database credentials
    host = input("MySQL Host (localhost): ") or "localhost"
    port = input("MySQL Port (3306): ") or "3306"
    user = input("MySQL User (root): ") or "root"
    password = input("MySQL Password: ")
    database = input("Database Name (customersdb): ") or "customersdb"
    
    try:
        connection = mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"✅ Connected to MySQL successfully!")
        print(f"📊 Found {len(tables)} tables in database '{database}'")
        
        if len(tables) == 0:
            print("⚠️  Database is empty. Consider running the data generator.")
        else:
            print("📋 Tables found:", [table[0] for table in tables])
        
        cursor.close()
        connection.close()
        
        # Update database.py with credentials
        update_database_config(host, port, user, password, database)
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   - Ensure MySQL server is running")
        print("   - Verify credentials are correct")
        print("   - Check if database exists")
        return False

def update_database_config(host, port, user, password, database):
    """Update database configuration in database.py"""
    print("\n🔧 Updating database configuration...")
    
    config_content = f"""
# Database configuration updated by start.py
DB_CONFIG = {{
    'host': '{host}',
    'port': {port},
    'user': '{user}',
    'password': '{password}',
    'database': '{database}',
    'charset': 'utf8mb4',
    'autocommit': True
}}
"""
    
    # Create or update .env file
    with open('.env', 'w') as f:
        f.write(f"DB_HOST={host}\n")
        f.write(f"DB_PORT={port}\n")
        f.write(f"DB_USER={user}\n")
        f.write(f"DB_PASSWORD={password}\n")
        f.write(f"DB_NAME={database}\n")
    
    print("✅ Configuration saved to .env file")

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    packages = [
        "streamlit>=1.47.1",
        "pandas>=2.3.1", 
        "plotly>=6.2.0",
        "mysql-connector-python>=9.4.0",
        "networkx>=3.5",
        "openpyxl>=3.1.5",
        "faker>=20.0.0"
    ]
    
    try:
        for package in packages:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
        
        print("✅ All dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def generate_sample_data():
    """Ask user if they want to generate sample data"""
    print("\n🎲 Sample Data Generation")
    print("Would you like to generate sample data for testing?")
    print("This will create 10,000+ records across all tables.")
    
    choice = input("Generate sample data? (y/N): ").lower()
    
    if choice in ['y', 'yes']:
        print("\n🔄 Generating sample data...")
        try:
            subprocess.run([sys.executable, "data_generator.py"], check=True)
            print("✅ Sample data generated successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate sample data: {e}")
            return False
    else:
        print("⏭️  Skipping sample data generation")
        return True

def launch_application():
    """Launch the Streamlit application"""
    print("\n🚀 Launching Database Explorer...")
    print("The application will open in your default web browser.")
    print("URL: http://localhost:5000")
    print("\n🛑 Press Ctrl+C to stop the application")
    print("=" * 60)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py", 
            "--server.port", "5000"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped. Thanks for using Database Explorer!")
    except Exception as e:
        print(f"❌ Failed to launch application: {e}")

def check_file_structure():
    """Verify all required files exist"""
    print("\n📁 Checking project files...")
    
    required_files = [
        "app.py", "database.py", "utils.py", "data_generator.py",
        "pages/1_Tables.py", "pages/2_Analytics.py", 
        "pages/3_Relationships.py", "pages/4_Export.py",
        ".streamlit/config.toml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def main():
    """Main setup and launch process"""
    print_header()
    
    # Step 1: Check Python version
    if not check_python_version():
        return
    
    # Step 2: Check file structure
    if not check_file_structure():
        print("\n❌ Please ensure all project files are in the current directory")
        return
    
    # Step 3: Install dependencies
    print("\n📦 Would you like to install/update dependencies?")
    install_deps = input("Install dependencies? (Y/n): ").lower()
    if install_deps not in ['n', 'no']:
        if not install_dependencies():
            return
    
    # Step 4: Test database connection
    if not check_mysql_connection():
        return
    
    # Step 5: Generate sample data (optional)
    if not generate_sample_data():
        return
    
    # Step 6: Launch application
    print("\n🎉 Setup complete! Ready to launch Database Explorer.")
    launch_now = input("Launch application now? (Y/n): ").lower()
    
    if launch_now not in ['n', 'no']:
        launch_application()
    else:
        print("\n✅ Setup complete!")
        print("To launch later, run: streamlit run app.py --server.port 5000")

if __name__ == "__main__":
    main()