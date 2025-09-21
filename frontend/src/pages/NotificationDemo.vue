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
    const response = await frappeRequest({
      method: 'gameplan.gameplan.api.notifications.get_user_notifications',
      params: {
        limit: 50
      }
    })
    
    if (response && response.message) {
      notifications.value = response.message
      console.log('Loaded notifications:', notifications.value.length)
    }
  } catch (error) {
    console.error('Error loading notifications:', error)
  } finally {
    loading.value = false
  }
}

const sendTestNotification = async () => {
  try {
    loading.value = true
    await frappeRequest({
      method: 'gameplan.gameplan.api.notifications.send_system_notification',
      params: {
        title: 'Test Notification',
        body: 'This is a test notification from Gameplan!',
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

const sendNotification = async (type) => {
  try {
    loading.value = true
    await frappeRequest({
      method: 'gameplan.gameplan.api.notifications.send_system_notification',
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
  if ('Notification' in window) {
    const permission = await Notification.requestPermission()
    permissionStatus.value = permission === 'granted' ? 'Granted' : 'Denied'
  } else {
    permissionStatus.value = 'Not Supported'
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
