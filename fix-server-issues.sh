#!/bin/bash

# Comprehensive fix for server issues
# Run this script on your production server

echo "=== Fixing Gameplan Server Issues ==="

# Navigate to frappe-bench directory
cd ~/frappe-bench/frappe-bench

echo "1. Updating Socket.IO CORS configuration..."

# Update Socket.IO CORS configuration in realtime/index.js
if [ -f "apps/frappe/realtime/index.js" ]; then
    sudo sed -i 's/origin: true,/origin: ["https:\/\/65.1.189.119", "http:\/\/65.1.189.119", "https:\/\/localhost", "http:\/\/localhost"],/g' apps/frappe/realtime/index.js
    echo "✓ Updated realtime/index.js CORS"
else
    echo "✗ realtime/index.js not found"
fi

# Update Socket.IO CORS configuration in socketio.js
if [ -f "apps/frappe/socketio.js" ]; then
    sudo sed -i 's/origin: true,/origin: ["https:\/\/65.1.189.119", "http:\/\/65.1.189.119", "https:\/\/localhost", "http:\/\/localhost"],/g' apps/frappe/socketio.js
    echo "✓ Updated socketio.js CORS"
else
    echo "✗ socketio.js not found"
fi

echo "2. Configuring Socket.IO port..."
bench set-config socketio_port 9000
echo "✓ Set socketio_port to 9000"

echo "3. Stopping existing processes..."
pkill -f socketio
pkill -f "node.*socketio"
sleep 3

echo "4. Starting Socket.IO server..."
nohup node apps/frappe/socketio.js > socketio.log 2>&1 &
sleep 5

echo "5. Checking Socket.IO status..."
if pgrep -f socketio > /dev/null; then
    echo "✓ Socket.IO is running"
    ps aux | grep socketio | grep -v grep
else
    echo "✗ Socket.IO failed to start"
    echo "Checking logs..."
    tail -20 socketio.log
fi

echo "6. Testing Socket.IO connection..."
curl -k "https://65.1.189.119/socket.io/?EIO=4&transport=polling" 2>/dev/null | head -c 100
echo ""

echo "7. Restarting Frappe services..."
bench restart

echo "8. Checking nginx configuration..."
if [ -f "/etc/nginx/sites-available/frappe" ]; then
    echo "✓ Nginx configuration exists"
    # Check if socket.io location block exists
    if grep -q "location /socket.io/" /etc/nginx/sites-available/frappe; then
        echo "✓ Socket.IO location block found in nginx"
    else
        echo "✗ Socket.IO location block missing in nginx"
        echo "Please add the following to your nginx configuration:"
        echo ""
        echo "    location /socket.io/ {"
        echo "        proxy_pass http://127.0.0.1:9000;"
        echo "        proxy_http_version 1.1;"
        echo "        proxy_set_header Upgrade \$http_upgrade;"
        echo "        proxy_set_header Connection \"upgrade\";"
        echo "        proxy_set_header Host \$host;"
        echo "        proxy_set_header X-Real-IP \$remote_addr;"
        echo "        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;"
        echo "        proxy_set_header X-Forwarded-Proto \$scheme;"
        echo "        proxy_cache_bypass \$http_upgrade;"
        echo "        proxy_read_timeout 86400;"
        echo "    }"
        echo ""
    fi
else
    echo "✗ Nginx configuration not found"
fi

echo "9. Testing API endpoints..."
echo "Testing spaces API..."
curl -k "https://65.1.189.119/api/v2/document/GP%20Project?start=0&limit=10" 2>/dev/null | head -c 200
echo ""

echo "10. Checking for errors in logs..."
if [ -f "logs/error.log" ]; then
    echo "Recent errors:"
    tail -10 logs/error.log
fi

if [ -f "socketio.log" ]; then
    echo "Socket.IO errors:"
    tail -10 socketio.log
fi

echo ""
echo "=== Fix Complete ==="
echo "If issues persist, check:"
echo "1. tail -f socketio.log"
echo "2. tail -f logs/error.log"
echo "3. Check nginx configuration includes Socket.IO location block"
echo "4. Verify firewall allows port 9000"
