#!/bin/bash

echo "=========================================="
echo "PostgreSQL Database Manager Setup (Ubuntu)"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. Consider running as a regular user."
fi

# Update package list
echo "Updating package list..."
sudo apt-get update

# Check if Python is installed
if command -v python3 &> /dev/null; then
    print_success "Python3 found"
    python3 --version
else
    print_error "Python3 is not installed"
    echo "Installing Python3..."
    sudo apt-get install -y python3
    if [ $? -eq 0 ]; then
        print_success "Python3 installed successfully"
    else
        print_error "Failed to install Python3"
        exit 1
    fi
fi

# Check if pip is installed
if command -v pip3 &> /dev/null; then
    print_success "pip3 found"
else
    print_error "pip3 is not installed"
    echo "Installing python3-pip..."
    sudo apt-get install -y python3-pip
    if [ $? -eq 0 ]; then
        print_success "pip3 installed successfully"
    else
        print_error "Failed to install pip3"
        exit 1
    fi
fi

# Install Python virtual environment (recommended)
if ! command -v python3-venv &> /dev/null; then
    echo "Installing python3-venv..."
    sudo apt-get install -y python3-venv
fi

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo
echo "Installing required Python packages..."
echo "=========================================="

packages=("streamlit" "psycopg2-binary" "pandas" "plotly" "sqlalchemy")

for package in "${packages[@]}"; do
    echo "Installing $package..."
    pip install $package
    if [ $? -eq 0 ]; then
        print_success "$package installed successfully"
    else
        print_error "Failed to install $package"
        exit 1
    fi
done

echo
echo "=========================================="
print_success "All packages installed successfully!"
echo "=========================================="
echo

# Check if PostgreSQL client tools are available (optional)
if command -v psql &> /dev/null; then
    print_success "PostgreSQL client tools found"
    psql --version
else
    print_warning "PostgreSQL client tools (psql) not found"
    echo "This is optional but recommended for advanced database operations"
    echo "You can install PostgreSQL client with:"
    echo "sudo apt-get install postgresql-client"
fi

echo
echo "=========================================="
print_success "Setup completed successfully!"
echo "=========================================="
echo
echo "Next steps:"
echo "1. Make sure your PostgreSQL server is running"
echo "2. Run the application using: ./run.sh"
echo "3. The application will open in your default web browser"
echo
echo "Default connection settings:"
echo "- Host: localhost"
echo "- Port: 5432"
echo "- Username: postgres"
echo "- Password: password"
echo
echo "You can modify these defaults by setting environment variables:"
echo "- PGHOST (default: localhost)"
echo "- PGPORT (default: 5432)"
echo "- PGUSER (default: postgres)"
echo "- PGPASSWORD (default: password)"
echo

# Make run script executable
chmod +x run.sh
print_success "Made run.sh executable"

echo
echo "Setup complete! You can now run: ./run.sh"
