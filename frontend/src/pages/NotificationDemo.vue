<template>
  <div class="notification-demo">
    <div class="max-w-4xl mx-auto p-6">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Notification System Demo</h1>
        <p class="text-gray-600">Test and demonstrate the real-time notification system</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-2 bg-blue-100 rounded-lg">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5-5-5h5v-5a7.5 7.5 0 0 0-15 0v5h5l-5 5-5-5h5v-5a7.5 7.5 0 0 0 15 0v5z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Total Notifications</p>
              <p class="text-2xl font-semibold text-gray-900">{{ notifications.length }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-2 bg-red-100 rounded-lg">
              <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Unread</p>
              <p class="text-2xl font-semibold text-gray-900">{{ unreadCount }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-2 bg-green-100 rounded-lg">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Permission</p>
              <p class="text-sm font-semibold" :class="webNotificationPermission === 'granted' ? 'text-green-600' : 'text-red-600'">
                {{ webNotificationPermission === 'granted' ? 'Granted' : 'Not Granted' }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="bg-white rounded-lg shadow p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Test Notifications</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Button
            @click="sendTestNotification"
            variant="solid"
            class="w-full"
            :loading="isLoading"
          >
            Send Test Notification
          </Button>

          <Button
            @click="requestNotificationPermission"
            variant="outline"
            class="w-full"
            v-if="webNotificationPermission !== 'granted'"
          >
            Request Permission
          </Button>

          <Button
            @click="markAllAsRead"
            variant="outline"
            class="w-full"
            v-if="unreadCount > 0"
          >
            Mark All as Read
          </Button>

          <Button
            @click="loadNotifications"
            variant="outline"
            class="w-full"
            :loading="isLoading"
          >
            Refresh
          </Button>
        </div>
      </div>

      <!-- Notification Types Demo -->
      <div class="bg-white rounded-lg shadow p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Send Different Notification Types</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Button
            @click="sendTaskAssignmentNotification"
            variant="outline"
            class="w-full"
          >
            Task Assignment
          </Button>

          <Button
            @click="sendTaskStatusChangeNotification"
            variant="outline"
            class="w-full"
          >
            Task Status Change
          </Button>

          <Button
            @click="sendTaskMovementNotification"
            variant="outline"
            class="w-full"
          >
            Task Movement
          </Button>

          <Button
            @click="sendSystemNotification"
            variant="outline"
            class="w-full"
          >
            System Notification
          </Button>
        </div>
      </div>

      <!-- Notifications Panel -->
      <div class="bg-white rounded-lg shadow">
        <div class="p-6 border-b border-gray-200">
          <h2 class="text-xl font-semibold text-gray-900">Recent Notifications</h2>
        </div>
        <NotificationsPanel :max-height="'500px'" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Button } from 'frappe-ui'
import { useNotifications } from '@/composables/useNotifications'
import { apiCall } from '@/utils/api'
import NotificationsPanel from '@/components/NotificationsPanel.vue'

// Composables
const {
  notifications,
  unreadCount,
  isLoading,
  webNotificationPermission,
  loadNotifications,
  markAllAsRead,
  requestNotificationPermission,
  sendTestNotification
} = useNotifications()

// Methods
const sendTaskAssignmentNotification = async () => {
  try {
    await apiCall('gameplan.gameplan.api.notifications.send_task_assignment_notification', {
        task_id: 'DEMO-001',
        task_title: 'Demo Task Assignment',
        assigned_to: window.$session?.user?.name || 'demo@example.com',
        assigned_by: 'admin@example.com',
        project: 'Demo Project',
        customer: 'Demo Customer',
        workflow_type: 'Sales Cycle'
      })
  } catch (error) {
    console.error('Error sending task assignment notification:', error)
  }
}

const sendTaskStatusChangeNotification = async () => {
  try {
    await apiCall('gameplan.gameplan.api.notifications.send_task_status_change_notification', {
        task_id: 'DEMO-002',
        task_title: 'Demo Status Change',
        from_status: 'Draft',
        to_status: 'In Progress',
        moved_by: window.$session?.user?.name || 'demo@example.com',
        project: 'Demo Project',
        customer: 'Demo Customer',
        workflow_type: 'Sales Cycle'
      })
  } catch (error) {
    console.error('Error sending task status change notification:', error)
  }
}

const sendTaskMovementNotification = async () => {
  try {
    await apiCall('gameplan.gameplan.api.notifications.send_task_bucket_movement_notification', {
        task_id: 'DEMO-003',
        task_title: 'Demo Task Movement',
        from_bucket: 'Backlog',
        to_bucket: 'In Progress',
        moved_by: window.$session?.user?.name || 'demo@example.com',
        project: 'Demo Project',
        customer: 'Demo Customer',
        workflow_type: 'Sales Cycle'
      })
  } catch (error) {
    console.error('Error sending task movement notification:', error)
  }
}

const sendSystemNotification = async () => {
  try {
    await apiCall('gameplan.gameplan.api.notifications.send_system_notification', {
        title: 'System Maintenance',
        body: 'The system will be undergoing maintenance in 30 minutes.',
        recipient_user: window.$session?.user?.name || 'demo@example.com'
    })
  } catch (error) {
    console.error('Error sending system notification:', error)
  }
}
</script>

<style scoped>
.notification-demo {
  @apply min-h-screen bg-gray-50;
}
</style>
