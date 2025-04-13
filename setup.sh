#!/bin/bash

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install setuptools
echo "Upgrading pip and installing setuptools..."
python3 -m pip install --upgrade pip setuptools wheel

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

# Create plots directory if it doesn't exist
mkdir -p plots

# Verify installation
echo "Verifying installation..."
python3 -c "import requests, pandas, matplotlib" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Setup complete! Virtual environment is activated."
    echo "To run the script, use: python3 crypto_metrics_tracker.py"
    echo "To deactivate the virtual environment when done, use: deactivate"
else
    echo "Error: Failed to install dependencies. Please check the requirements.txt file."
    exit 1
fi 