#!/bin/bash

echo "Starting Flask backend on port 3000..."

# Kill any existing process on port 3000
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Add user Python bin to PATH
export PATH=$PATH:/Users/matvejgrevcov/Library/Python/3.9/bin

# Run with gunicorn
gunicorn --bind 0.0.0.0:3000 --workers 1 wsgi:app