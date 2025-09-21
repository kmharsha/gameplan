#!/bin/bash

# Setup Socket.IO for production deployment
# Run this script on your production server

echo "Setting up Socket.IO for production..."

# Navigate to frappe-bench directory
cd ~/frappe-bench/frappe-bench

# Update Socket.IO CORS configuration
echo "Updating Socket.IO CORS configuration..."
sudo sed -i 's/origin: true,/origin: ["https:\/\/65.1.189.119", "http:\/\/65.1.189.119"],/g' apps/frappe/realtime/index.js

# Verify the change
echo "Verifying CORS configuration..."
grep -A 3 -B 3 "origin:" apps/frappe/realtime/index.js

# Update socketio_port in common_site_config.json
echo "Updating socketio_port configuration..."
bench set-config socketio_port 9000

# Verify the configuration
echo "Verifying socketio_port configuration..."
cat sites/common_site_config.json | grep socketio_port

# Stop any existing Socket.IO processes
echo "Stopping existing Socket.IO processes..."
pkill -f socketio

# Start Socket.IO server
echo "Starting Socket.IO server..."
nohup node apps/frappe/socketio.js > socketio.log 2>&1 &

# Wait a moment for the server to start
sleep 2

# Check if Socket.IO is running
echo "Checking Socket.IO status..."
ps aux | grep socketio | grep -v grep

# Test the connection
echo "Testing Socket.IO connection..."
curl -k "https://65.1.189.119/socket.io/?EIO=4&transport=polling" 2>/dev/null | head -c 100
echo ""

echo "Socket.IO setup complete!"
echo "Check the logs with: tail -f socketio.log"
