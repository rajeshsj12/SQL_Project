#!/bin/bash

echo "=========================================="
echo "PostgreSQL Database Manager"
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

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed"
    echo "Please run setup.sh first to install dependencies"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
fi

# Check if streamlit is installed
python3 -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "Streamlit is not installed"
    echo "Please run setup.sh first to install dependencies"
    exit 1
fi

print_success "Starting PostgreSQL Database Manager..."
echo
echo "The application will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the application"
echo "=========================================="
echo

# Start the Streamlit application
streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
