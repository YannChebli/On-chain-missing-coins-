#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup first..."
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Run the script
python3 crypto_metrics_tracker.py

# Deactivate virtual environment when done
deactivate 