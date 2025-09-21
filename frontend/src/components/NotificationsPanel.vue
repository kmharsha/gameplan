<template>
  <div class="notifications-panel">
    <!-- Header -->
    <div class="notifications-header">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900">Notifications</h3>
        <div class="flex items-center space-x-2">
          <Button
            v-if="unreadCount > 0"
            @click="markAllAsRead"
            variant="ghost"
            size="sm"
            class="text-xs"
          >
            Mark all as read
          </Button>
          <Button
            @click="loadNotifications"
            variant="ghost"
            size="sm"
            class="text-xs"
            :loading="isLoading"
          >
            Refresh
          </Button>
        </div>
      </div>
      
      <!-- Unread count badge -->
      <div v-if="unreadCount > 0" class="mt-2">
        <Badge variant="solid" class="bg-red-500 text-white">
          {{ unreadCount }} unread
        </Badge>
      </div>
    </div>

    <!-- Notification permission banner -->
    <div 
      v-if="isWebNotificationSupported && webNotificationPermission !== 'granted'"
      class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
          <span class="text-sm text-blue-800">
            Enable browser notifications for real-time updates
          </span>
        </div>
        <Button
          @click="requestNotificationPermission"
          variant="ghost"
          size="sm"
          class="text-blue-600 hover:text-blue-800"
        >
          Enable
        </Button>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading && notifications.length === 0" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
      <p class="mt-2 text-sm text-gray-500">Loading notifications...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="text-center py-8">
      <div class="text-red-500 mb-2">
        <svg class="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
      <p class="text-sm text-gray-500">{{ error }}</p>
      <Button @click="loadNotifications" variant="ghost" size="sm" class="mt-2">
        Try again
      </Button>
    </div>

    <!-- Empty state -->
    <div v-else-if="notifications.length === 0" class="text-center py-8">
      <div class="text-gray-400 mb-2">
        <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5-5-5h5v-5a7.5 7.5 0 0 0-15 0v5h5l-5 5-5-5h5v-5a7.5 7.5 0 0 0 15 0v5z"></path>
        </svg>
      </div>
      <p class="text-sm text-gray-500">No notifications yet</p>
      <Button @click="sendTestNotification" variant="ghost" size="sm" class="mt-2">
        Send test notification
      </Button>
    </div>

    <!-- Notifications list -->
    <div v-else class="notifications-list">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="notification-item"
        :class="{
          'unread': !notification.is_read,
          'read': notification.is_read
        }"
        @click="handleNotificationClick(notification)"
      >
        <div class="notification-content">
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <h4 class="notification-title">{{ notification.title }}</h4>
              <p class="notification-body">{{ notification.body }}</p>
              
              <!-- Notification type badge -->
              <div class="mt-1">
                <Badge 
                  :variant="getNotificationTypeVariant(notification.notification_type)"
                  class="text-xs"
                >
                  {{ notification.notification_type }}
                </Badge>
              </div>
              
              <!-- Reference link -->
              <div v-if="notification.reference_doctype && notification.reference_name" class="mt-2">
                <span class="text-xs text-gray-500">
                  {{ notification.reference_doctype }}: {{ notification.reference_name }}
                </span>
              </div>
            </div>
            
            <!-- Unread indicator -->
            <div v-if="!notification.is_read" class="ml-2">
              <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
            </div>
          </div>
          
          <!-- Timestamp -->
          <div class="mt-2 text-xs text-gray-400">
            {{ formatTime(notification.created_at) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Load more button -->
    <div v-if="notifications.length > 0" class="mt-4 text-center">
      <Button
        @click="loadMoreNotifications"
        variant="ghost"
        size="sm"
        :loading="isLoading"
      >
        Load more
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useNotifications, type Notification } from '../composables/useNotifications'
import { Button, Badge } from 'frappe-ui'

// Props
interface Props {
  maxHeight?: string
  showHeader?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  maxHeight: '400px',
  showHeader: true
})

// Composables
const {
  notifications,
  unreadCount,
  isLoading,
  error,
  isWebNotificationSupported,
  webNotificationPermission,
  loadNotifications,
  markAsRead,
  markAllAsRead,
  requestNotificationPermission,
  sendTestNotification
} = useNotifications()

// State
const currentLimit = ref(20)

// Methods
const handleNotificationClick = async (notification: Notification) => {
  // Mark as read if unread
  if (!notification.is_read) {
    await markAsRead(notification.id)
  }
  
  // Navigate to reference document if available
  if (notification.reference_doctype && notification.reference_name) {
    // This would need to be implemented based on your routing
    console.log('Navigate to:', notification.reference_doctype, notification.reference_name)
    // Example: router.push(`/g/${notification.reference_doctype.toLowerCase()}/${notification.reference_name}`)
  }
}

const loadMoreNotifications = async () => {
  currentLimit.value += 20
  await loadNotifications(currentLimit.value)
}

const getNotificationTypeVariant = (type: string) => {
  const variants: Record<string, string> = {
    'Task Assignment': 'solid',
    'Task Status Change': 'subtle',
    'Task Movement': 'subtle',
    'Project Update': 'solid',
    'Discussion': 'outline',
    'Comment': 'outline',
    'System': 'solid',
    'Custom': 'outline'
  }
  return variants[type] || 'outline'
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  
  return date.toLocaleDateString()
}

// Computed
const panelStyle = computed(() => ({
  maxHeight: props.maxHeight,
  overflowY: 'auto'
}))
</script>

<style scoped>
.notifications-panel {
  @apply bg-white rounded-lg shadow-sm border border-gray-200;
}

.notifications-header {
  @apply p-4 border-b border-gray-200;
}

.notification-item {
  @apply p-4 border-b border-gray-100 cursor-pointer transition-colors;
}

.notification-item:hover {
  @apply bg-gray-50;
}

.notification-item.unread {
  @apply bg-blue-50 border-l-4 border-l-blue-500;
}

.notification-item.read {
  @apply bg-white;
}

.notification-title {
  @apply text-sm font-medium text-gray-900 truncate;
}

.notification-body {
  @apply text-sm text-gray-600 mt-1 line-clamp-2;
}

.notifications-list {
  @apply divide-y divide-gray-100;
}

/* Custom scrollbar */
.notifications-panel::-webkit-scrollbar {
  width: 4px;
}

.notifications-panel::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.notifications-panel::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.notifications-panel::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
