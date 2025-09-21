// Cross-Platform Notification Service
// Supports desktop browsers, mobile browsers, and PWA

interface NotificationOptions {
  title: string
  body: string
  icon?: string
  badge?: string
  tag?: string
  data?: any
  requireInteraction?: boolean
  actions?: NotificationAction[]
}

interface DeviceInfo {
  id: string
  type: 'desktop' | 'mobile' | 'pwa'
  userAgent: string
  isOnline: boolean
  lastSeen: Date
}

class CrossPlatformNotificationService {
  private isSupported: boolean = false
  private permission: NotificationPermission = 'default'
  private registration: ServiceWorkerRegistration | null = null
  private deviceId: string = ''
  private isPWA: boolean = false

  constructor() {
    this.initialize()
  }

  private async initialize() {
    console.log('Initializing Cross-Platform Notification Service...')
    
    // Check if notifications are supported
    this.isSupported = 'Notification' in window
    
    if (!this.isSupported) {
      console.log('Notifications not supported in this browser')
      return
    }

    // Check if PWA is installed
    this.isPWA = window.matchMedia('(display-mode: standalone)').matches || 
                 (window.navigator as any).standalone === true

    // Generate device ID
    this.deviceId = this.generateDeviceId()
    
    // Register service worker for PWA support
    if ('serviceWorker' in navigator) {
      try {
        this.registration = await navigator.serviceWorker.register('/sw.js')
        console.log('Service Worker registered:', this.registration)
      } catch (error) {
        console.log('Service Worker registration failed:', error)
      }
    }

    // Check current permission
    this.permission = Notification.permission
    
    console.log('Notification Service initialized:', {
      supported: this.isSupported,
      permission: this.permission,
      isPWA: this.isPWA,
      deviceId: this.deviceId
    })
  }

  private generateDeviceId(): string {
    let deviceId = localStorage.getItem('gameplan-device-id')
    if (!deviceId) {
      deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
      localStorage.setItem('gameplan-device-id', deviceId)
    }
    return deviceId
  }

  async requestPermission(): Promise<NotificationPermission> {
    if (!this.isSupported) {
      throw new Error('Notifications not supported')
    }

    try {
      this.permission = await Notification.requestPermission()
      console.log('Permission requested:', this.permission)
      return this.permission
    } catch (error) {
      console.error('Permission request failed:', error)
      throw error
    }
  }

  async showNotification(options: NotificationOptions): Promise<void> {
    if (!this.isSupported) {
      throw new Error('Notifications not supported')
    }

    if (this.permission !== 'granted') {
      throw new Error('Notification permission not granted')
    }

    try {
      // Try to show browser notification
      const notification = new Notification(options.title, {
        body: options.body,
        icon: options.icon || '/favicon.png',
        badge: options.badge || '/favicon.png',
        tag: options.tag || 'gameplan-notification',
        data: options.data,
        requireInteraction: options.requireInteraction || false,
        actions: options.actions || []
      })

      // Handle notification events
      notification.onclick = () => {
        console.log('Notification clicked')
        window.focus()
        notification.close()
      }

      notification.onerror = (error) => {
        console.error('Notification error:', error)
      }

      // Auto-close after 10 seconds
      setTimeout(() => {
        notification.close()
      }, 10000)

      console.log('Browser notification shown:', notification)
      
      // Also send to service worker for PWA
      if (this.registration && this.isPWA) {
        await this.sendToServiceWorker(options)
      }

    } catch (error) {
      console.error('Failed to show notification:', error)
      throw error
    }
  }

  private async sendToServiceWorker(options: NotificationOptions): Promise<void> {
    if (!this.registration) return

    try {
      await this.registration.showNotification(options.title, {
        body: options.body,
        icon: options.icon || '/favicon.png',
        badge: options.badge || '/favicon.png',
        tag: options.tag || 'gameplan-notification',
        data: options.data,
        requireInteraction: options.requireInteraction || false,
        actions: options.actions || []
      })
      console.log('Service Worker notification sent')
    } catch (error) {
      console.error('Service Worker notification failed:', error)
    }
  }

  // Send notification to all devices of a user
  async sendToAllDevices(userId: string, options: NotificationOptions): Promise<void> {
    try {
      // This would typically call your backend API
      // which then sends to all registered devices
      console.log('Sending notification to all devices for user:', userId)
      
      // For now, just show locally
      await this.showNotification(options)
      
    } catch (error) {
      console.error('Failed to send to all devices:', error)
      throw error
    }
  }

  // Register device for push notifications
  async registerDevice(userId: string): Promise<void> {
    try {
      const deviceInfo: DeviceInfo = {
        id: this.deviceId,
        type: this.isPWA ? 'pwa' : this.isMobile() ? 'mobile' : 'desktop',
        userAgent: navigator.userAgent,
        isOnline: navigator.onLine,
        lastSeen: new Date()
      }

      // Send device info to backend
      console.log('Registering device:', deviceInfo)
      
      // This would typically call your backend API
      // to register the device for push notifications
      
    } catch (error) {
      console.error('Device registration failed:', error)
      throw error
    }
  }

  private isMobile(): boolean {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  }

  // Get device capabilities
  getCapabilities() {
    return {
      supported: this.isSupported,
      permission: this.permission,
      isPWA: this.isPWA,
      isMobile: this.isMobile(),
      deviceId: this.deviceId,
      serviceWorker: !!this.registration
    }
  }

  // Test notification
  async testNotification(): Promise<void> {
    await this.showNotification({
      title: 'Test Cross-Platform Notification',
      body: 'This notification works on desktop, mobile, and PWA!',
      tag: 'test-cross-platform',
      requireInteraction: true
    })
  }
}

// Export singleton instance
export const crossPlatformNotifications = new CrossPlatformNotificationService()
export default crossPlatformNotifications
