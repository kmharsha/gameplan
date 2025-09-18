# Socket.IO Deployment Instructions

## Files Updated Locally

1. **Frontend Socket Configuration**: `frontend/src/socket.js`
   - Updated to handle production environments better
   - Uses HTTPS and same port as web server in production
   - Added better error handling and connection options

2. **Nginx Configuration Template**: `nginx-socketio.conf`
   - Complete nginx configuration with Socket.IO support
   - Replace `YOUR_DOMAIN_OR_IP` with your actual domain/IP

3. **Setup Script**: `setup-socketio.sh`
   - Automated script to configure Socket.IO on production server

## Deployment Steps

### 1. Push Changes to Server
```bash
# Push all changes to your server
git add .
git commit -m "Fix Socket.IO configuration for production"
git push origin your-branch
```

### 2. On Production Server

#### Option A: Use the Setup Script
```bash
# Navigate to your gameplan app directory
cd /path/to/your/frappe-bench/apps/gameplan

# Run the setup script
./setup-socketio.sh
```

#### Option B: Manual Setup
```bash
# Navigate to frappe-bench
cd ~/frappe-bench/frappe-bench

# Update CORS configuration
sudo sed -i 's/origin: true,/origin: ["https:\/\/65.1.189.119", "http:\/\/65.1.189.119"],/g' apps/frappe/realtime/index.js

# Update socketio_port
bench set-config socketio_port 9000

# Stop existing processes
pkill -f socketio

# Start Socket.IO
nohup node apps/frappe/socketio.js > socketio.log 2>&1 &
```

### 3. Configure Nginx

```bash
# Edit your nginx site configuration
sudo nano /etc/nginx/sites-available/frappe

# Replace the content with the template from nginx-socketio.conf
# Make sure to replace YOUR_DOMAIN_OR_IP with 65.1.189.119

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Test the Setup

```bash
# Test Socket.IO endpoint
curl -k "https://65.1.189.119/socket.io/?EIO=4&transport=polling"

# Check Socket.IO process
ps aux | grep socketio

# Check logs
tail -f socketio.log
```

## Expected Results

After deployment:
- ✅ No more 404 errors in browser console
- ✅ No more "Invalid origin" errors
- ✅ "Socket connected" message in console
- ✅ Real-time features working

## Troubleshooting

If you still see issues:

1. **Check Socket.IO process**: `ps aux | grep socketio`
2. **Check logs**: `tail -f socketio.log`
3. **Test endpoint**: `curl -k "https://65.1.189.119/socket.io/?EIO=4&transport=polling"`
4. **Check nginx**: `sudo nginx -t`
5. **Hard refresh browser**: Ctrl+F5

## Files to Commit

Make sure to commit these files:
- `frontend/src/socket.js` (updated)
- `nginx-socketio.conf` (new)
- `setup-socketio.sh` (new)
- `SOCKETIO_DEPLOYMENT.md` (new)
