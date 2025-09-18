import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { onNotification, offNotification } from '../socket'
import { apiCall } from '@/utils/api'
import { notificationService } from '../services/notificationService'

export interface Notification {
  id: string
  title: string
  body: string
  notification_type: string
  reference_doctype?: string
  reference_name?: string
  data?: any
  created_at: string
  is_read?: boolean
  read_at?: string
}

export function useNotifications() {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Notification service
  const isWebNotificationSupported = notificationService.isSupported()
  const webNotificationPermission = ref(notificationService.getPermissionStatus())

  // Load notifications from server
  const loadNotifications = async (limit = 50, unreadOnly = false) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiCall('gameplan.gameplan.api.notifications.get_user_notifications', {
        limit,
        unread_only: unreadOnly
      })
      
      notifications.value = response.message || []
    } catch (err) {
      console.error('Error loading notifications:', err)
      error.value = 'Failed to load notifications'
    } finally {
      isLoading.value = false
    }
  }

  // Load unread count
  const loadUnreadCount = async () => {
    try {
      const response = await apiCall('gameplan.gameplan.api.notifications.get_unread_count')
      unreadCount.value = response.message || 0
    } catch (err) {
      console.error('Error loading unread count:', err)
    }
  }

  // Mark notification as read
  const markAsRead = async (notificationId: string) => {
    try {
      await apiCall('gameplan.gameplan.api.notifications.mark_notification_as_read', {
        notification_id: notificationId
      })
      
      // Update local state
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification) {
        notification.is_read = true
        notification.read_at = new Date().toISOString()
      }
      
      // Update unread count
      await loadUnreadCount()
    } catch (err) {
      console.error('Error marking notification as read:', err)
    }
  }

  // Mark all notifications as read
  const markAllAsRead = async () => {
    try {
      await apiCall('gameplan.gameplan.api.notifications.mark_all_notifications_as_read')
      
      // Update local state
      notifications.value.forEach(notification => {
        notification.is_read = true
        notification.read_at = new Date().toISOString()
      })
      
      unreadCount.value = 0
    } catch (err) {
      console.error('Error marking all notifications as read:', err)
    }
  }

  // Handle real-time notification
  const handleRealtimeNotification = async (notification: Notification) => {
    // Add to beginning of notifications array
    notifications.value.unshift(notification)
    
    // Update unread count
    if (!notification.is_read) {
      unreadCount.value++
    }
    
    // Show notification using the service
    await notificationService.showNotification(notification)
  }

  // Show browser notification
  const showBrowserNotification = (notification: Notification) => {
    if (!isWebNotificationSupported) return
    
    const browserNotification = new Notification(notification.title, {
      body: notification.body,
      icon: '/favicon.png',
      tag: notification.id,
      data: notification
    })
    
    // Handle click on notification
    browserNotification.onclick = () => {
      window.focus()
      browserNotification.close()
      
      // Navigate to reference document if available
      if (notification.reference_doctype && notification.reference_name) {
        // This would need to be implemented based on your routing
        console.log('Navigate to:', notification.reference_doctype, notification.reference_name)
      }
    }
    
    // Auto close after 5 seconds
    setTimeout(() => {
      browserNotification.close()
    }, 5000)
  }

  // Request notification permission
  const requestNotificationPermission = async () => {
    try {
      console.log('Requesting notification permission...')
      const granted = await notificationService.requestPermission()
      webNotificationPermission.value = notificationService.getPermissionStatus()
      console.log('Permission granted:', granted, 'Status:', webNotificationPermission.value)
      return granted
    } catch (err) {
      console.error('Error requesting notification permission:', err)
      return false
    }
  }

  // Send test notification
  const sendTestNotification = async () => {
    try {
      await apiCall('gameplan.gameplan.api.notifications.test_notification')
    } catch (err) {
      console.error('Error sending test notification:', err)
    }
  }

  // Setup real-time listener
  let unsubscribe: (() => void) | null = null

  onMounted(async () => {
    // Initialize notification service
    await notificationService.initialize()
    
    // Load initial data
    loadNotifications()
    loadUnreadCount()
    
    // Request notification permission
    if (isWebNotificationSupported && webNotificationPermission.value === 'default') {
      requestNotificationPermission()
    }
    
    // Setup real-time listener
    unsubscribe = onNotification(handleRealtimeNotification)
  })

  onUnmounted(() => {
    if (unsubscribe) {
      unsubscribe()
    }
  })

  return {
    // State
    notifications,
    unreadCount,
    isLoading,
    error,
    isWebNotificationSupported,
    webNotificationPermission,
    
    // Methods
    loadNotifications,
    loadUnreadCount,
    markAsRead,
    markAllAsRead,
    requestNotificationPermission,
    sendTestNotification,
    showBrowserNotification
  }
}
