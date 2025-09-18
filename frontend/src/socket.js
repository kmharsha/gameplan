import { io } from 'socket.io-client'
import { socketio_port } from '../../../../sites/common_site_config.json'
import { getCachedListResource } from 'frappe-ui/src/resources/listResource'
import { getCachedResource } from 'frappe-ui/src/resources/resources'

let socket = null
let notificationCallbacks = []

export function initSocket() {
  let host = window.location.hostname
  let siteName = window.site_name
  
  // For production, use the same port as the web server (HTTPS)
  // For development, use the socketio port
  let port = ''
  let protocol = window.location.protocol === 'https:' ? 'https' : 'http'
  
  // Only add socketio port for development
  if (window.location.protocol === 'http:' && window.location.hostname !== 'localhost') {
    port = `:${socketio_port}`
  }
  
  let url = `${protocol}://${host}${port}/${siteName}`

  console.log('Socket.IO connecting to:', url)

  socket = io(url, {
    withCredentials: true,
    reconnectionAttempts: 5,
    transports: ['polling', 'websocket'],
    timeout: 20000,
    forceNew: true
  })
  
  // Handle resource refetch
  socket.on('refetch_resource', (data) => {
    if (data.cache_key) {
      let resource = getCachedResource(data.cache_key) || getCachedListResource(data.cache_key)
      if (resource) {
        resource.reload()
      }
    }
  })

  // Handle new notifications
  socket.on('new_notification', (notification) => {
    console.log('New notification received:', notification)
    
    // Call all registered notification callbacks
    notificationCallbacks.forEach(callback => {
      try {
        callback(notification)
      } catch (error) {
        console.error('Error in notification callback:', error)
      }
    })
  })

  // Handle connection events
  socket.on('connect', () => {
    console.log('Socket connected')
  })

  socket.on('disconnect', () => {
    console.log('Socket disconnected')
  })

  socket.on('connect_error', (error) => {
    console.error('Socket connection error:', error)
  })

  return socket
}

export function useSocket() {
  return socket
}

export function onNotification(callback) {
  notificationCallbacks.push(callback)
  
  // Return unsubscribe function
  return () => {
    const index = notificationCallbacks.indexOf(callback)
    if (index > -1) {
      notificationCallbacks.splice(index, 1)
    }
  }
}

export function offNotification(callback) {
  const index = notificationCallbacks.indexOf(callback)
  if (index > -1) {
    notificationCallbacks.splice(index, 1)
  }
}
