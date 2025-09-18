# Real-time Push Notifications System

This document describes the real-time push notification system implemented in Gameplan using Frappe Framework (Python) and Vue.js.

## Overview

The notification system provides:
- Real-time notifications using Frappe's WebSocket + Redis
- Browser push notifications for web users
- Mobile push notifications for Capacitor/Cordova apps
- Task movement notifications (e.g., when tasks are moved to g/sales-bucket)
- Admin interface for sending notifications from Frappe backend
- Complete notification history and management

## Architecture

### Backend (Frappe/Python)
- **GP Notification Log**: Stores all notifications
- **GP Notification Sender**: Admin interface for sending notifications
- **NotificationManager**: Utility class for sending notifications
- **Real-time Publishing**: Uses `frappe.publish_realtime` for WebSocket events

### Frontend (Vue.js)
- **Socket.io Client**: Connects to Frappe's WebSocket server
- **useNotifications Composable**: Manages notification state and API calls
- **NotificationsPanel Component**: Displays notification list
- **NotificationBell Component**: Header notification bell with unread count
- **NotificationService**: Handles both web and mobile notifications

## Features

### 1. Real-time Notifications
- Automatic notifications when tasks are created, updated, or moved
- Real-time updates via WebSocket connection
- No third-party services required (uses Frappe's built-in WebSocket)

### 2. Browser Push Notifications
- Web Notifications API integration
- Permission handling
- Click-to-navigate functionality
- Auto-dismiss after 5 seconds

### 3. Mobile Notifications
- Capacitor Local Notifications support
- Push notification support (when configured)
- In-app notification display

### 4. Task Movement Notifications
- Notifications when tasks move between statuses
- Special notifications for bucket movements (sales/procurement)
- Notifications when tasks are assigned

### 5. Admin Interface
- Send notifications from Frappe backend
- Bulk notification sending
- Notification scheduling
- Statistics and analytics

## Usage Examples

### 1. Sending a Notification from Backend

```python
from gameplan.utils.notifications import NotificationManager

# Send to specific user
NotificationManager.send_custom_notification(
    title="New Task Assigned",
    body="Task ID: TASK-001 has been assigned to you",
    recipient_user="user@example.com"
)

# Send to role
NotificationManager.send_notification(
    title="System Maintenance",
    body="System will be down for maintenance",
    notification_type="System",
    recipient_role="All"
)

# Send task movement notification
NotificationManager.send_task_movement_notification(
    task_doc=task_document,
    from_bucket="Backlog",
    to_bucket="In Progress",
    moved_by="admin@example.com"
)
```

### 2. Using Notifications in Vue.js

```vue
<template>
  <div>
    <!-- Notification Bell -->
    <NotificationBell />
    
    <!-- Notifications Panel -->
    <NotificationsPanel :max-height="'400px'" />
  </div>
</template>

<script setup>
import { useNotifications } from '@/composables/useNotifications'
import NotificationBell from '@/components/NotificationBell.vue'
import NotificationsPanel from '@/components/NotificationsPanel.vue'

const { 
  notifications, 
  unreadCount, 
  markAsRead, 
  sendTestNotification 
} = useNotifications()
</script>
```

### 3. Sending Notifications from Frontend

```javascript
import { sendTaskStatusChangeNotification } from '@/utils/taskNotifications'

// Send notification when task status changes
await sendTaskStatusChangeNotification({
  taskId: 'TASK-001',
  taskTitle: 'Design Review',
  fromStatus: 'Draft',
  toStatus: 'In Progress',
  movedBy: 'user@example.com',
  project: 'Project Alpha',
  customer: 'Customer ABC'
})
```

### 4. API Methods

```javascript
// Get user notifications
const notifications = await frappeRequest({
  method: 'gameplan.api.notifications.get_user_notifications',
  params: { limit: 50, unread_only: false }
})

// Mark notification as read
await frappeRequest({
  method: 'gameplan.api.notifications.mark_notification_as_read',
  params: { notification_id: 'NOTIF-001' }
})

// Send custom notification
await frappeRequest({
  method: 'gameplan.api.notifications.send_custom_notification',
  params: {
    title: 'Custom Notification',
    body: 'This is a custom notification',
    recipient_user: 'user@example.com'
  }
})
```

## Configuration

### 1. Backend Configuration

The notification system uses Frappe's built-in WebSocket server. No additional configuration is required.

### 2. Frontend Configuration

The socket connection is automatically configured in `frontend/src/socket.js`:

```javascript
import { initSocket, onNotification } from './socket'

// Initialize socket
const socket = initSocket()

// Listen for notifications
onNotification((notification) => {
  console.log('New notification:', notification)
})
```

### 3. Mobile Configuration

For mobile apps, install the required Capacitor plugins:

```bash
npm install @capacitor/local-notifications
npm install @capacitor/push-notifications
```

## Notification Types

The system supports the following notification types:

1. **Task Assignment**: When a task is assigned to a user
2. **Task Status Change**: When a task status changes
3. **Task Movement**: When a task moves between buckets/statuses
4. **Project Update**: When a project is updated
5. **Discussion**: New discussion created
6. **Comment**: New comment added
7. **System**: System notifications
8. **Custom**: Custom notifications

## Task Movement Notifications

The system automatically sends notifications for:

- Task status changes (Draft → In Progress → Completed)
- Task assignments
- Movement to sales bucket (when sales tasks are completed)
- Movement from procurement bucket (when procurement tasks are started)
- Project updates

## Admin Interface

### GP Notification Sender

Use this DocType to send notifications from the Frappe backend:

1. Go to GP Notification Sender
2. Fill in the notification details
3. Choose recipient (user, role, or all users)
4. Set reference document if applicable
5. Send immediately or schedule for later

### GP Notification Dashboard

View notification statistics and analytics:

- Total notifications sent
- Notifications by type
- Read/unread statistics
- Recent notifications
- Top recipients
- Notification trends

## Testing

### Send Test Notification

```javascript
// From frontend
await sendTestNotification()

// From backend
frappe.call('gameplan.api.notifications.test_notification')
```

### Test Real-time Connection

1. Open browser developer tools
2. Check console for "Socket connected" message
3. Send a test notification
4. Verify notification appears in real-time

## Troubleshooting

### Common Issues

1. **Notifications not appearing**: Check WebSocket connection in browser console
2. **Permission denied**: Ensure user has proper permissions for GP Notification Log
3. **Mobile notifications not working**: Check Capacitor plugin installation and permissions

### Debug Mode

Enable debug logging by adding to browser console:

```javascript
localStorage.setItem('debug', 'socket.io-client:*')
```

## Security

- All notifications are user-scoped
- Role-based notifications respect user permissions
- API methods include proper permission checks
- Sensitive data is not exposed in notifications

## Performance

- Notifications are stored in database for history
- Real-time events are published via Redis
- Frontend uses efficient Vue.js reactivity
- Mobile notifications use native APIs

## Future Enhancements

- Email notification integration
- Push notification service integration (FCM, APNS)
- Notification templates
- Advanced scheduling options
- Notification preferences per user
- Rich media notifications
