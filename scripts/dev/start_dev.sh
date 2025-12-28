#!/bin/bash
# Start both backend and frontend for development

set -e  # Exit on error

echo "========================================"
echo "Starting Development Servers"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python 3 not found. Please install Python 3."
        exit 1
    else
        PYTHON_CMD=python
    fi
else
    PYTHON_CMD=python3
fi

echo "Python found: $($PYTHON_CMD --version)"

# Check if Node is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js not found. Please install Node.js."
    exit 1
fi

echo "Node.js found: $(node --version)"
echo ""

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

# Check Python dependencies
if ! $PYTHON_CMD -c "import flask" 2>/dev/null; then
    echo "Installing Python dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt
fi

# Install concurrently if not installed
if ! npm list concurrently &> /dev/null 2>&1; then
    echo "Installing concurrently..."
    npm install --save-dev concurrently
fi

echo ""
echo "========================================"
echo "Starting Servers"
echo "========================================"
echo ""
echo "Backend (Flask):  http://localhost:8080"
echo "Frontend (React): http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start both servers using concurrently
npm run start:dev

