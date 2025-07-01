#!/bin/bash

# Start script for Render deployment
echo "Starting Telegram Bot Application..."

# Check if required environment variables are set
if [ -z "$BOT_TOKEN" ]; then
    echo "ERROR: BOT_TOKEN environment variable is not set!"
    exit 1
fi

if [ -z "$ADMIN_ID" ]; then
    echo "ERROR: ADMIN_ID environment variable is not set!"
    exit 1
fi

# Print environment info (without sensitive data)
echo "Python version: $(python --version)"
echo "Admin ID: $ADMIN_ID"
echo "API Secret Key: $(echo $API_SECRET_KEY | cut -c1-10)..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the application
echo "Starting main application..."
python main.py

# If main.py exits, log the reason
echo "Application exited with code $?"
