/**
 * Notification service for handling web notifications
 * Mobile support can be added later when needed
 */

export interface NotificationData {
  id: string
  title: string
  body: string
  notification_type: string
  reference_doctype?: string
  reference_name?: string
  data?: any
  created_at: string
}

class NotificationService {
  private isInitialized = false
  private isWebNotificationSupported = 'Notification' in window
  private webNotificationPermission = 'default'

  async initialize() {
    if (this.isInitialized) return

    await this.initializeWeb()
    this.isInitialized = true
  }

  private async initializeWeb() {
    if (!this.isWebNotificationSupported) {
      console.log('Web notifications not supported')
      return
    }

    this.webNotificationPermission = Notification.permission

    if (this.webNotificationPermission === 'default') {
      this.webNotificationPermission = await Notification.requestPermission()
    }
  }

  async showNotification(notification: NotificationData) {
    await this.showWebNotification(notification)
  }

  private async showWebNotification(notification: NotificationData) {
    if (!this.isWebNotificationSupported || this.webNotificationPermission !== 'granted') {
      return
    }

    try {
      const browserNotification = new Notification(notification.title, {
        body: notification.body,
        icon: '/favicon.png',
        tag: notification.id,
        data: notification,
        requireInteraction: false
      })

      // Handle click
      browserNotification.onclick = () => {
        window.focus()
        browserNotification.close()
        this.handleNotificationClick(notification)
      }

      // Auto close after 5 seconds
      setTimeout(() => {
        browserNotification.close()
      }, 5000)

    } catch (error) {
      console.error('Error showing web notification:', error)
    }
  }

  async requestPermission(): Promise<boolean> {
    console.log('NotificationService: Checking if web notifications are supported:', this.isWebNotificationSupported)
    if (!this.isWebNotificationSupported) {
      console.log('NotificationService: Web notifications not supported')
      return false
    }
    
    try {
      console.log('NotificationService: Requesting permission...')
      this.webNotificationPermission = await Notification.requestPermission()
      console.log('NotificationService: Permission result:', this.webNotificationPermission)
      return this.webNotificationPermission === 'granted'
    } catch (error) {
      console.error('NotificationService: Error requesting notification permission:', error)
      return false
    }
  }

  getPermissionStatus(): string {
    return this.webNotificationPermission
  }

  isSupported(): boolean {
    return this.isWebNotificationSupported
  }

  private handleNotificationClick(notification: NotificationData) {
    // Navigate to the referenced document
    if (notification.reference_doctype && notification.reference_name) {
      // This would need to be implemented based on your routing
      console.log('Navigate to:', notification.reference_doctype, notification.reference_name)
      // Example: router.push(`/g/${notification.reference_doctype.toLowerCase()}/${notification.reference_name}`)
    }
  }

  private async sendTokenToServer(token: string) {
    try {
      // Send the push token to your server
      // This would be implemented based on your API
      console.log('Sending token to server:', token)
      // await frappeRequest({
      //   method: 'gameplan.api.notifications.register_push_token',
      //   params: { token }
      // })
    } catch (error) {
      console.error('Error sending token to server:', error)
    }
  }
}

// Export singleton instance
export const notificationService = new NotificationService()
export default notificationService