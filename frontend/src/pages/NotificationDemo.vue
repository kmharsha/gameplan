<template>
  <div class="notification-demo">
    <div class="header">
      <h1>Notification System Demo</h1>
      <p>Test and demonstrate the real-time notification system</p>
    </div>

    <!-- Notification Summary Cards -->
    <div class="summary-cards">
      <div class="card">
        <div class="icon">🔔</div>
        <div class="content">
          <h3>Total Notifications</h3>
          <p class="count">{{ notifications.length }}</p>
        </div>
      </div>
      <div class="card">
        <div class="icon">⚠️</div>
        <div class="content">
          <h3>Unread</h3>
          <p class="count">{{ unreadCount }}</p>
        </div>
      </div>
      <div class="card">
        <div class="icon">✅</div>
        <div class="content">
          <h3>Permission</h3>
          <p class="status">{{ permissionStatus }}</p>
        </div>
      </div>
    </div>

    <!-- Test Notifications -->
    <div class="section">
      <h2>Test Notifications</h2>
      <div class="buttons">
        <button @click="sendTestNotification" :disabled="loading" class="btn btn-primary">
          {{ loading ? 'Sending...' : 'Send Test Notification' }}
        </button>
        <button @click="requestPermission" class="btn btn-secondary">
          Request Permission
        </button>
        <button @click="testBrowserNotification" class="btn btn-success">
          Test Browser Popup
        </button>
        <button @click="refreshNotifications" class="btn btn-secondary">
          Refresh
        </button>
      </div>
    </div>

    <!-- Send Different Notification Types -->
    <div class="section">
      <h2>Send Different Notification Types</h2>
      <div class="notification-types">
        <button @click="sendNotification('Task Assignment')" class="btn btn-dark">Task Assignment</button>
        <button @click="sendNotification('Task Status Change')" class="btn btn-dark">Task Status Change</button>
        <button @click="sendNotification('Task Movement')" class="btn btn-dark">Task Movement</button>
        <button @click="sendNotification('System Notification')" class="btn btn-dark">System Notification</button>
      </div>
    </div>

    <!-- Recent Notifications -->
    <div class="section">
      <h2>Recent Notifications</h2>
      <div class="notifications-header">
        <span>Notifications</span>
        <button @click="refreshNotifications" class="btn btn-small">Refresh</button>
      </div>
      
      <div class="notifications-list">
        <div v-if="notifications.length === 0" class="empty-state">
          <p>No notifications yet</p>
        </div>
        <div v-else class="notification-item" v-for="notification in notifications" :key="notification.id">
          <div class="notification-content">
            <h4>{{ notification.title }}</h4>
            <p>{{ notification.body }}</p>
            <div class="notification-meta">
              <span class="type">{{ notification.type }}</span>
              <span class="time">{{ formatTime(notification.created_at) }}</span>
              <span v-if="!notification.is_read" class="unread">Unread</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { frappeRequest } from 'frappe-ui'

// Reactive data
const notifications = ref([])
const loading = ref(false)
const permissionStatus = ref('Checking...')

// Computed properties
const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.is_read).length
})

// Methods
const loadNotifications = async () => {
  try {
    loading.value = true
    console.log('Loading notifications...')
    console.log('Current user from window:', window.user)
    console.log('Session user from frappe:', window.frappe?.session?.user)
    
    const response = await frappeRequest({
      url: '/api/method/gameplan.gameplan.api.notifications.get_user_notifications',
      params: {
        limit: 50
      }
    })
    
    console.log('Notification API response:', response)
    console.log('Response type:', typeof response)
    console.log('Response message:', response?.message)
    console.log('Response is array:', Array.isArray(response))
    console.log('Response length:', response?.length)
    console.log('Response constructor:', response?.constructor?.name)
    
    // Handle both response.message and direct response
    let notificationData = null
    if (response && response.message) {
      console.log('Using response.message')
      notificationData = response.message
    } else if (Array.isArray(response)) {
      console.log('Using direct response array')
      notificationData = response
    } else {
      console.log('Response is neither message nor array, checking if it has length property')
      if (response && response.length !== undefined) {
        console.log('Response has length property, treating as array')
        notificationData = response
      }
    }
    
    console.log('Final notificationData:', notificationData)
    console.log('notificationData type:', typeof notificationData)
    console.log('notificationData is array:', Array.isArray(notificationData))
    console.log('notificationData length:', notificationData?.length)
    
    if (notificationData && notificationData.length > 0) {
      notifications.value = notificationData
      console.log('Loaded notifications:', notifications.value.length)
      console.log('Notifications data:', notifications.value)
    } else {
      console.log('No notifications found or invalid response')
      console.log('Response structure:', Object.keys(response || {}))
    }
  } catch (error) {
    console.error('Error loading notifications:', error)
    console.error('Error details:', error.response || error.message)
    alert('Error loading notifications: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const sendTestNotification = async () => {
  try {
    loading.value = true
    console.log('Sending test notification...')
    
    // Try to send notification to current user instead of Administrator
    const currentUser = window.user?.name || 'Administrator'
    console.log('Current user:', currentUser)
    console.log('Window user object:', window.user)
    
    const response = await frappeRequest({
      url: '/api/method/gameplan.gameplan.api.notifications.send_system_notification',
      params: {
        title: 'Test Notification',
        body: 'This is a test notification from Gameplan!',
        recipient_user: currentUser
      }
    })
    
    console.log('Test notification API response:', response)
    console.log('Test notification sent successfully')
    
    // Test browser notification immediately
    console.log('Checking notification permission:', Notification.permission)
    if (Notification.permission === 'granted') {
      console.log('Permission granted, showing browser notification...')
      try {
        const notification = new Notification('Test Browser Notification', {
          body: 'This is a test browser notification from Gameplan!',
          icon: '/favicon.png',
          tag: 'test-notification-' + Date.now(),
          requireInteraction: false
        })
        
        console.log('Browser notification created:', notification)
        
        // Handle click
        notification.onclick = () => {
          console.log('Browser notification clicked')
          window.focus()
          notification.close()
        }
        
        // Auto close after 5 seconds
        setTimeout(() => {
          notification.close()
          console.log('Browser notification auto-closed')
        }, 5000)
        
      } catch (error) {
        console.error('Error creating browser notification:', error)
        alert('Error creating browser notification: ' + error.message)
      }
    } else {
      console.log('Browser notification permission not granted:', Notification.permission)
      alert('Browser notification permission not granted. Please click "Request Permission" first.')
    }
    
    // Wait a moment for the notification to be created
    setTimeout(async () => {
      console.log('Refreshing notifications after delay...')
      await loadNotifications()
    }, 1000)
    
  } catch (error) {
    console.error('Error sending notification:', error)
    console.error('Error details:', error.response || error.message)
    alert('Error sending notification: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const sendNotification = async (type) => {
  try {
    loading.value = true
    await frappeRequest({
      url: '/api/method/gameplan.gameplan.api.notifications.send_system_notification',
      params: {
        title: type,
        body: `This is a ${type} notification`,
        recipient_user: 'Administrator'
      }
    })
    
    // Refresh notifications after sending
    await loadNotifications()
  } catch (error) {
    console.error('Error sending notification:', error)
  } finally {
    loading.value = false
  }
}

const requestPermission = async () => {
  console.log('Requesting notification permission...')
  console.log('Notification API available:', 'Notification' in window)
  
  if ('Notification' in window) {
    try {
      const permission = await Notification.requestPermission()
      console.log('Permission result:', permission)
      permissionStatus.value = permission === 'granted' ? 'Granted' : 'Denied'
      
      // Test browser notification if permission granted
      if (permission === 'granted') {
        console.log('Permission granted, showing test notification...')
        try {
          const notification = new Notification('Test Browser Notification', {
            body: 'This is a test browser notification!',
            icon: '/favicon.png',
            tag: 'test-notification',
            requireInteraction: false
          })
          
          console.log('Test notification created:', notification)
          
          // Handle click
          notification.onclick = () => {
            console.log('Test notification clicked')
            window.focus()
            notification.close()
          }
          
          // Auto close after 5 seconds
          setTimeout(() => {
            notification.close()
            console.log('Test notification auto-closed')
          }, 5000)
          
        } catch (error) {
          console.error('Error creating test notification:', error)
          alert('Error creating test notification: ' + error.message)
        }
      } else {
        console.log('Permission denied or dismissed')
        alert('Notification permission was denied. Please enable notifications in your browser settings.')
      }
    } catch (error) {
      console.error('Error requesting permission:', error)
      alert('Error requesting notification permission: ' + error.message)
    }
  } else {
    console.log('Notifications not supported in this browser')
    permissionStatus.value = 'Not Supported'
    alert('Browser notifications are not supported in this browser.')
  }
}

const testBrowserNotification = () => {
  console.log('Testing browser notification directly...')
  console.log('Notification API available:', 'Notification' in window)
  console.log('Current permission:', Notification.permission)
  
  if (!('Notification' in window)) {
    alert('Browser notifications are not supported in this browser.')
    return
  }
  
  if (Notification.permission === 'granted') {
    console.log('Permission already granted, showing test notification...')
    try {
      const notification = new Notification('Direct Test Notification', {
        body: 'This is a direct test of browser notifications!',
        icon: '/favicon.png',
        tag: 'direct-test-' + Date.now(),
        requireInteraction: false
      })
      
      console.log('Direct test notification created:', notification)
      
      // Handle click
      notification.onclick = () => {
        console.log('Direct test notification clicked')
        window.focus()
        notification.close()
      }
      
      // Auto close after 5 seconds
      setTimeout(() => {
        notification.close()
        console.log('Direct test notification auto-closed')
      }, 5000)
      
    } catch (error) {
      console.error('Error creating direct test notification:', error)
      alert('Error creating direct test notification: ' + error.message)
    }
  } else if (Notification.permission === 'denied') {
    alert('Notification permission is denied. Please enable notifications in your browser settings and refresh the page.')
  } else {
    alert('Notification permission not requested yet. Please click "Request Permission" first.')
  }
}

const refreshNotifications = () => {
  loadNotifications()
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

// Lifecycle
onMounted(() => {
  loadNotifications()
  
  // Check notification permission
  if ('Notification' in window) {
    permissionStatus.value = Notification.permission === 'granted' ? 'Granted' : 'Not Granted'
  } else {
    permissionStatus.value = 'Not Supported'
  }
})
</script>

<style scoped>
.notification-demo {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.header p {
  color: #666;
  font-size: 1.1rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.card .icon {
  font-size: 2rem;
}

.card .content h3 {
  margin: 0 0 5px 0;
  font-size: 1rem;
  color: #666;
}

.card .count {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
}

.card .status {
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0;
  color: #28a745;
}

.section {
  margin-bottom: 30px;
}

.section h2 {
  margin-bottom: 15px;
  color: #333;
}

.buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.notification-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-dark {
  background: #343a40;
  color: white;
}

.btn-dark:hover {
  background: #23272b;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover {
  background: #218838;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-small {
  padding: 5px 10px;
  font-size: 0.9rem;
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.notifications-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  max-height: 400px;
  overflow-y: auto;
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: #666;
}

.notification-item {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-content h4 {
  margin: 0 0 5px 0;
  color: #333;
}

.notification-content p {
  margin: 0 0 10px 0;
  color: #666;
}

.notification-meta {
  display: flex;
  gap: 15px;
  font-size: 0.9rem;
}

.notification-meta .type {
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 12px;
  color: #495057;
}

.notification-meta .time {
  color: #666;
}

.notification-meta .unread {
  background: #dc3545;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: bold;
}
</style>
