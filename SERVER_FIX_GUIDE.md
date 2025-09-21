# Server Fix Guide for Gameplan

This guide addresses the server issues you're experiencing with push notifications and Socket.IO connections.

## Issues Identified

1. **Socket.IO "Invalid origin" error** - CORS configuration not allowing your server IP
2. **API 500 errors** - Likely related to notification system or permissions
3. **Frontend connection issues** - Socket.js configuration not optimized for production

## Quick Fix (Run on Server)

### Step 1: Run the Comprehensive Fix Script

```bash
# On your production server
cd /path/to/your/frappe-bench/apps/gameplan
chmod +x fix-server-issues.sh
./fix-server-issues.sh
```

### Step 2: Update Nginx Configuration

If the script indicates nginx configuration issues, update your nginx config:

```bash
sudo nano /etc/nginx/sites-available/frappe
```

Add this location block **before** the main location block:

```nginx
# Socket.IO configuration - MUST be before the main location block
location /socket.io/ {
    proxy_pass http://127.0.0.1:9000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
    proxy_read_timeout 86400;
}
```

Then reload nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Step 3: Check Notification System

```bash
# Run the notification system check
cd /path/to/your/frappe-bench
bench --site your-site-name console
```

In the console, run:
```python
exec(open('/path/to/your/frappe-bench/apps/gameplan/check-notification-system.py').read())
```

## Manual Fixes (If Script Doesn't Work)

### Fix 1: Socket.IO CORS Configuration

```bash
cd ~/frappe-bench/frappe-bench

# Update CORS in realtime/index.js
sudo sed -i 's/origin: true,/origin: ["https:\/\/65.1.189.119", "http:\/\/65.1.189.119"],/g' apps/frappe/realtime/index.js

# Update CORS in socketio.js (if exists)
sudo sed -i 's/origin: true,/origin: ["https:\/\/65.1.189.119", "http:\/\/65.1.189.119"],/g' apps/frappe/socketio.js
```

### Fix 2: Configure Socket.IO Port

```bash
bench set-config socketio_port 9000
```

### Fix 3: Restart Services

```bash
# Stop existing processes
pkill -f socketio

# Start Socket.IO
nohup node apps/frappe/socketio.js > socketio.log 2>&1 &

# Restart Frappe
bench restart
```

## Verification

### Test Socket.IO Connection

```bash
curl -k "https://65.1.189.119/socket.io/?EIO=4&transport=polling"
```

Should return Socket.IO handshake data, not an error.

### Test API Endpoints

```bash
curl -k "https://65.1.189.119/api/v2/document/GP%20Project?start=0&limit=10"
```

Should return JSON data, not 500 error.

### Check Logs

```bash
# Socket.IO logs
tail -f socketio.log

# Frappe error logs
tail -f logs/error.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

## Frontend Changes Made

1. **Updated socket.js** - Fixed production connection logic for HTTPS
   - Development: Uses socketio port (e.g., `http://localhost:9000/site-name`)
   - Production: Uses same port as web server (e.g., `https://65.1.189.119/site-name`)
   - Nginx proxies `/socket.io/` requests to Socket.IO server on port 9000
2. **Improved error handling** - Better connection options
3. **CORS compatibility** - Works with server configuration

## Common Issues and Solutions

### Issue: "Invalid origin" error persists
**Solution**: Check that nginx is properly proxying `/socket.io/` requests to port 9000

### Issue: API 500 errors continue
**Solution**: Check Frappe error logs and ensure notification system permissions are correct

### Issue: Socket connection fails
**Solution**: Verify Socket.IO process is running on port 9000 and firewall allows the port

### Issue: Frontend still shows errors
**Solution**: Clear browser cache and check browser console for specific error messages

## Files Modified

1. `frontend/src/socket.js` - Improved production connection logic
2. `nginx-socketio.conf` - Updated with your server IP
3. `setup-socketio.sh` - Enhanced setup script
4. `fix-server-issues.sh` - Comprehensive fix script (new)
5. `check-notification-system.py` - Notification system checker (new)

## Next Steps

1. Run the fix script on your server
2. Update nginx configuration if needed
3. Test the connection from your browser
4. Check logs for any remaining issues
5. If problems persist, check the specific error messages in browser console and server logs

## Support

If you continue to have issues after following this guide, please provide:
1. Output from the fix script
2. Browser console errors
3. Server logs (socketio.log and error.log)
4. Nginx configuration status
