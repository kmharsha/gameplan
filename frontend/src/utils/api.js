/**
 * API utility for making direct fetch calls to Frappe backend
 * This provides better control over headers, CSRF tokens, and error handling
 */

export class ApiError extends Error {
  constructor(message, status, response) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.response = response
  }
}

/**
 * Make a direct API call to Frappe backend
 * @param {string} method - The API method path (e.g. 'gameplan.api.create_artwork')
 * @param {Object} data - The data to send
 * @param {Object} options - Additional options
 * @returns {Promise<any>} The API response
 */
export async function apiCall(method, data = {}, options = {}) {
  const {
    httpMethod = 'POST',
    baseUrl = '',
    timeout = 30000,
    useFormData = false
  } = options

  const url = `${baseUrl}/api/method/${method}`
  
  console.log(`[API] Calling ${httpMethod} ${url} with data:`, data)

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)

  let body
  let contentType
  
  if (httpMethod === 'GET') {
    body = undefined
    contentType = undefined
  } else if (useFormData) {
    // Use form parameters for better type handling
    const formData = new URLSearchParams()
    Object.entries(data).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        formData.append(key, String(value))
      }
    })
    body = formData
    contentType = 'application/x-www-form-urlencoded'
  } else {
    body = JSON.stringify(data)
    contentType = 'application/json'
  }

  try {
    const response = await fetch(url, {
      method: httpMethod,
      credentials: 'include',
      headers: {
        ...(contentType && { 'Content-Type': contentType }),
        'X-Frappe-CSRF-Token': window.csrf_token || '',
        ...options.headers
      },
      body,
      signal: controller.signal
    })

    clearTimeout(timeoutId)

    console.log(`[API] Raw response for ${method}:`, {
      status: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries(response.headers.entries())
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error(`[API] HTTP error for ${method}:`, response.status, errorText)
      throw new ApiError(
        `HTTP ${response.status}: ${errorText || response.statusText}`,
        response.status,
        response
      )
    }

    const result = await response.json()
    console.log(`[API] Success response for ${method}:`, result)

    // Frappe typically wraps the actual data in a 'message' property
    return result.message !== undefined ? result.message : result

  } catch (error) {
    clearTimeout(timeoutId)
    
    if (error.name === 'AbortError') {
      console.error(`[API] Request timeout for ${method}`)
      throw new ApiError(`Request timeout after ${timeout}ms`, 408)
    }
    
    if (error instanceof ApiError) {
      throw error
    }
    
    console.error(`[API] Network/JSON error for ${method}:`, error)
    throw new ApiError(`Network error: ${error.message}`, 0, error)
  }
}

/**
 * Artwork API methods
 */
export const artworkApi = {
  // Create a new artwork
  async createArtwork(data) {
    // Ensure numeric fields are properly typed and use form data for better type handling
    const processedData = {
      ...data,
      estimated_hours: data.estimated_hours !== undefined ? parseFloat(data.estimated_hours) : 0,
      budget: data.budget !== undefined ? parseFloat(data.budget) : 0
    }
    return apiCall('gameplan.api.create_artwork', processedData, { useFormData: true })
  },

  // Update an existing artwork
  async updateArtwork(artworkName, data) {
    return apiCall('gameplan.api.update_artwork', {
      artwork_name: artworkName,
      ...data
    })
  },

  // Get artworks for a customer
  async getCustomerArtworks(customer) {
    return apiCall('gameplan.api.get_customer_artworks', {
      customer: String(customer)
    })
  },

  // Create an artwork task
  async createArtworkTask(data) {
    return apiCall('gameplan.api.create_artwork_task', data)
  },

  // Create a Sales Cycle artwork task
  async createSalesTask(data) {
    return apiCall('gameplan.api.create_sales_cycle_task', data)
  },

  // Create a Procurement Cycle artwork task
  async createProcurementTask(data) {
    return apiCall('gameplan.api.create_procurement_cycle_task', data)
  },

  // Get artwork tasks
  async getArtworkTasks(filters = {}) {
    return apiCall('gameplan.api.get_artwork_tasks', filters)
  },

  // Get available task transitions
  async getTaskTransitions(taskName) {
    return apiCall('gameplan.api.get_artwork_task_transitions', {
      task_name: taskName
    })
  },

  // Update artwork task status
  async updateTaskStatus(taskName, status, reason = '', comments = '') {
    return apiCall('gameplan.api.update_artwork_task_status', {
      task_name: taskName,
      new_status: status,
      reason,
      comments
    })
  },

  // Get kanban data
  async getKanbanData() {
    return apiCall('gameplan.api.get_artwork_kanban_data')
  },

  // Get approved tasks
  async getApprovedTasks(searchTerm = '') {
    return apiCall('gameplan.api.get_approved_artwork_tasks', {
      search_term: searchTerm
    })
  },

  // Get task details
  async getTaskDetails(taskName) {
    return apiCall('gameplan.api.get_artwork_task_details', {
      task_name: taskName
    })
  },

  // Get related tasks (sales/procurement connections)
  async getRelatedTasks(taskName) {
    return apiCall('gameplan.api.get_related_tasks', {
      task_name: taskName
    })
  },

  // Create procurement task from completed sales task
  async createProcurementTaskFromSales(salesTaskName) {
    return apiCall('gameplan.api.create_procurement_task_from_sales', {
      sales_task_name: salesTaskName
    })
  }
}

/**
 * Test API connectivity
 */
export async function testApiConnection() {
  try {
    const result = await apiCall('gameplan.api.test_api')
    console.log('[API] Connection test successful:', result)
    return result
  } catch (error) {
    console.error('[API] Connection test failed:', error)
    throw error
  }
}
