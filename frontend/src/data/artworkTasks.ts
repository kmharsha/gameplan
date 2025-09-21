import { reactive, ref, computed } from 'vue'
import { createDocumentResource, createListResource, call } from 'frappe-ui'
import { artworkApi, apiCall } from '@/utils/api'
import { 
  sendTaskStatusChangeNotification, 
  sendTaskMovedFromProcurementBucketNotification 
} from '../utils/taskNotifications'

// Main artwork tasks list - Sales Tasks
export const salesTasks = createListResource({
  doctype: 'GP Sales Task',
  fields: ['name', 'title', 'status', 'artwork', 'customer', 'assigned_to', 'priority', 'modified', 'owner'],
  filters: {},
  orderBy: 'modified desc',
  pageLength: 20,
  auto: true,
})

// Main artwork tasks list - Procurement Tasks
export const procurementTasks = createListResource({
  doctype: 'GP Procurement Task',
  fields: ['name', 'title', 'status', 'artwork', 'customer', 'assigned_to', 'priority', 'modified', 'owner'],
  filters: {},
  orderBy: 'modified desc',
  pageLength: 20,
  auto: true,
})

// Combined artwork tasks for backward compatibility
export const artworkTasks = {
  data: computed(() => [
    ...(salesTasks.data.value || []).map(task => ({ ...task, workflow_type: 'Sales Cycle' })),
    ...(procurementTasks.data.value || []).map(task => ({ ...task, workflow_type: 'Procurement Cycle' }))
  ]),
  reload: () => {
    salesTasks.reload()
    procurementTasks.reload()
  }
}

// Workflow type constants
export const WORKFLOW_TYPES = {
  SALES: 'Sales Cycle',
  PROCUREMENT: 'Procurement Cycle'
}

export const SALES_STATUSES = ['Draft', 'Quality Review', 'Rework', 'Completed']
export const PROCUREMENT_STATUSES = ['Procurement Draft', 'Procurement Review', 'Procurement Rework', 'Final Approved']

// Workflow type helpers
export function getWorkflowStatuses(workflowType: string): string[] {
  if (workflowType === WORKFLOW_TYPES.SALES) {
    return SALES_STATUSES
  } else if (workflowType === WORKFLOW_TYPES.PROCUREMENT) {
    return PROCUREMENT_STATUSES
  }
  return [...SALES_STATUSES, ...PROCUREMENT_STATUSES]
}

export function isValidStatusForWorkflow(status: string, workflowType: string): boolean {
  const validStatuses = getWorkflowStatuses(workflowType)
  return validStatuses.includes(status)
}

// Kanban data for artwork tasks
export function useArtworkKanban() {
  const kanbanData = ref({})
  const loading = ref(false)
  const error = ref(null)

  const fetchKanbanData = async () => {
    console.log('[ArtworkKanban] fetchKanbanData called')
    loading.value = true
    error.value = null
    
    try {
      console.log('[ArtworkKanban] Calling artworkApi.getKanbanData()...')
      const data = await artworkApi.getKanbanData()
      console.log('[ArtworkKanban] Raw kanban data received:', data)
      console.log('[ArtworkKanban] Data type:', typeof data)
      console.log('[ArtworkKanban] Data keys:', Object.keys(data || {}))
      
      // Clear existing data first to ensure reactivity
      console.log('[ArtworkKanban] Clearing existing kanbanData...')
      kanbanData.value = {}
      
      // Use nextTick to ensure the clear is processed before setting new data
      await new Promise(resolve => setTimeout(resolve, 0))
      
      // Set new data
      console.log('[ArtworkKanban] Setting new kanbanData...')
      kanbanData.value = { ...data }
      console.log('[ArtworkKanban] kanbanData.value after setting:', kanbanData.value)
      
      // Debug: Log all tasks with their customer info
      Object.entries(data || {}).forEach(([status, tasks]) => {
        console.log(`[ArtworkKanban] Status ${status}:`, tasks.length, 'tasks')
        tasks.forEach((task, index) => {
          if (index < 3) { // Log first 3 tasks for each status
            console.log(`[ArtworkKanban] Task ${index + 1}:`, {
              name: task.name,
              title: task.title,
              customer: task.customer,
              customer_title: task.customer_title,
              status: task.status,
              workflow_type: task.workflow_type
            })
          }
        })
      })
    } catch (err) {
      error.value = err.message
      console.error('[ArtworkKanban] Error fetching kanban data:', err)
      console.error('[ArtworkKanban] Error details:', {
        message: err.message,
        stack: err.stack,
        response: err.response
      })
    } finally {
      loading.value = false
      console.log('[ArtworkKanban] fetchKanbanData completed, loading:', loading.value)
    }
  }

  const moveTask = async (taskName: string, newStatus: string, reason?: string, comments?: string) => {
    try {
      // Get task details before moving
      const taskDetails = await artworkApi.getTaskDetails(taskName)
      const oldStatus = taskDetails?.status
      
      await artworkApi.updateTaskStatus(taskName, newStatus, reason || '', comments || '')
      
      // Send notification for status change
      if (oldStatus && oldStatus !== newStatus) {
        await sendTaskStatusChangeNotification({
          taskId: taskName,
          taskTitle: taskDetails?.title || 'Unknown Task',
          fromStatus: oldStatus,
          toStatus: newStatus,
          movedBy: window.$session?.user?.name || 'Unknown User',
          project: taskDetails?.project,
          customer: taskDetails?.customer,
          workflowType: taskDetails?.workflow_type
        })
      }
      
      // Refresh kanban data after successful move
      await fetchKanbanData()
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  return {
    kanbanData,
    loading,
    error,
    fetchKanbanData,
    moveTask
  }
}

// Individual artwork task details
export function useArtworkTask(taskId: string) {
  const taskDetails = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchTaskDetails = async () => {
    if (!taskId) return
    
    loading.value = true
    error.value = null
    
    try {
      const data = await artworkApi.getTaskDetails(taskId)
      taskDetails.value = data
    } catch (err) {
      error.value = err.message
      console.error('Error fetching task details:', err)
    } finally {
      loading.value = false
    }
  }

  const updateStatus = async (newStatus: string, reason?: string, comments?: string) => {
    try {
      await artworkApi.updateTaskStatus(taskId, newStatus, reason || '', comments || '')
      
      // Refresh task details
      await fetchTaskDetails()
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const addComment = async (content: string, attachments?: string) => {
    try {
      const params = {
        task_name: taskId,
        content: content
      }
      
      if (attachments) {
        params.attachments = attachments
      }
      
      const comment = await apiCall('gameplan.api.add_artwork_task_comment', params)
      
      // Refresh task details to get updated comments
      await fetchTaskDetails()
      return comment
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const addAttachment = async (fileUrl: string, fileName: string, version?: string, description?: string) => {
    try {
      // Determine doctype based on task details
      const doctype = taskDetails.value?.task?.workflow_type === 'Sales Cycle' ? 'GP Sales Task' : 'GP Procurement Task'
      
      const task = createDocumentResource({
        doctype: doctype,
        name: taskId
      })
      
      await task.setValue.submit({
        attachments: [
          ...(taskDetails.value?.task?.attachments || []),
          {
            file_name: fileName,
            file_url: fileUrl,
            version: version || '1.0',
            description: description || '',
            uploaded_by: '',
            upload_date: new Date().toISOString()
          }
        ]
      })
      
      // Refresh task details
      await fetchTaskDetails()
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const getAvailableTransitions = async () => {
    try {
      const transitions = await artworkApi.getTaskTransitions(taskId)
      return transitions
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  return {
    taskDetails,
    loading,
    error,
    fetchTaskDetails,
    updateStatus,
    addComment,
    addAttachment,
    getAvailableTransitions
  }
}

// Approved artwork tasks for reporting
export function useApprovedArtworkTasks() {
  const approvedTasks = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchApprovedTasks = async (searchTerm: string = '') => {
    loading.value = true
    error.value = null
    
    try {
      const data = await artworkApi.getApprovedTasks(searchTerm)
      approvedTasks.value = data
    } catch (err) {
      error.value = err.message
      console.error('Error fetching approved tasks:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    approvedTasks,
    loading,
    error,
    fetchApprovedTasks
  }
}

// Bucket tasks for Procurement team
export function useBucketTasks() {
  const bucketTasks = ref([])
  const loading = ref(false)
  const error = ref(null)
  const stats = ref(null)

  const fetchBucketTasks = async (customerFilter = null, sortBy = 'cycle_count', sortOrder = 'desc') => {
    loading.value = true
    error.value = null
    
    try {
      const data = await apiCall('gameplan.api.get_bucket_tasks', {
        customer_filter: customerFilter,
        sort_by: sortBy,
        sort_order: sortOrder
      })
      console.log('[useBucketTasks] Raw API response:', data)
      
      // Handle the response format - data might be an array or an object with tasks property
      if (Array.isArray(data)) {
        bucketTasks.value = data
      } else if (data && data.tasks) {
        bucketTasks.value = data.tasks
      } else {
        bucketTasks.value = []
      }
      
      console.log('[useBucketTasks] Processed bucketTasks:', bucketTasks.value)
    } catch (err) {
      error.value = err.message
      console.error('Error fetching bucket tasks:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchCompletedSalesTasks = async (customerFilter = null, artworkTitleFilter = null, artworkFilter = null, sortBy = 'modified', sortOrder = 'desc', limitStart = 0, limitPageLength = 20) => {
    loading.value = true
    error.value = null
    
    try {
      console.log('[fetchCompletedSalesTasks] Calling API with params:', {
        customer_filter: customerFilter,
        artwork_title_filter: artworkTitleFilter,
        artwork_filter: artworkFilter,
        sort_by: sortBy,
        sort_order: sortOrder,
        limit_start: limitStart,
        limit_page_length: limitPageLength
      })
      
      const data = await apiCall('gameplan.api.get_completed_sales_tasks', {
        customer_filter: customerFilter,
        artwork_title_filter: artworkTitleFilter,
        artwork_filter: artworkFilter,
        sort_by: sortBy,
        sort_order: sortOrder,
        limit_start: limitStart,
        limit_page_length: limitPageLength
      })
      
      console.log('[fetchCompletedSalesTasks] Raw API response:', data)
      return data || { tasks: [], total_count: 0, has_more: false }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching completed sales tasks:', err)
      return { tasks: [], total_count: 0, has_more: false }
    } finally {
      loading.value = false
    }
  }

  const moveCompletedSalesToBucket = async (taskName) => {
    try {
      const result = await apiCall('gameplan.api.move_completed_sales_to_bucket', {
        task_name: taskName
      })
      return result
    } catch (err) {
      console.error('Error moving completed sales to bucket:', err)
      throw err
    }
  }

  const fetchBucketStats = async () => {
    try {
      const data = await apiCall('gameplan.api.get_bucket_stats')
      stats.value = data
    } catch (err) {
      console.error('Error fetching bucket stats:', err)
    }
  }

  const moveFromBucket = async (taskName, newStatus = 'Procurement Review') => {
    try {
      // Get task details before moving
      const taskDetails = await artworkApi.getTaskDetails(taskName)
      
      await apiCall('gameplan.api.move_task_from_bucket', {
        task_name: taskName,
        new_status: newStatus
      })
      
      // Send notification for bucket movement
      await sendTaskMovedFromProcurementBucketNotification({
        taskId: taskName,
        taskTitle: taskDetails?.title || 'Unknown Task',
        newStatus: newStatus,
        movedBy: window.$session?.user?.name || 'Unknown User',
        project: taskDetails?.project,
        customer: taskDetails?.customer
      })
      
      // Refresh bucket tasks after successful move
      await fetchBucketTasks()
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  return {
    bucketTasks,
    loading,
    error,
    stats,
    fetchBucketTasks,
    fetchBucketStats,
    moveFromBucket,
    fetchCompletedSalesTasks,
    moveCompletedSalesToBucket
  }
}

// Create new artwork task
export function useCreateArtworkTask() {
  const loading = ref(false)
  const error = ref(null)

  const createTask = async (title: string, artwork: string, description: string = '', priority: string = 'Medium', workflowType: string = 'Sales Cycle') => {
    loading.value = true
    error.value = null
    
    try {
      const task = await artworkApi.createArtworkTask({
        title,
        artwork,
        description,
        priority,
        workflow_type: workflowType
      })
      
      // Refresh appropriate task list based on workflow type
      if (workflowType === 'Sales Cycle') {
        salesTasks.reload()
      } else {
        procurementTasks.reload()
      }
      
      return task
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const createSalesTask = async (title: string, artwork: string, description: string = '', priority: string = 'Medium') => {
    return createTask(title, artwork, description, priority, 'Sales Cycle')
  }

  const createProcurementTask = async (title: string, artwork: string, description: string = '', priority: string = 'Medium') => {
    return createTask(title, artwork, description, priority, 'Procurement Cycle')
  }

  return {
    loading,
    error,
    createTask,
    createSalesTask,
    createProcurementTask
  }
}

// Status transition helpers for unified workflow system
export const STATUS_COLORS = {
  // Common statuses
  'Draft': 'bg-ink-gray-3',
  'Completed': 'bg-green-200',
  'Rework': 'bg-orange-100',
  
  // Sales Cycle specific
  'Quality Review': 'bg-blue-100',
  
  // Procurement Cycle specific
  'Bucket': 'bg-yellow-100',
  'Procurement Draft': 'bg-ink-gray-3',
  'Procurement Review': 'bg-purple-100',
  'Procurement Rework': 'bg-orange-100',
  'Final Approved': 'bg-green-100'
}

export const STATUS_TEXT_COLORS = {
  // Common statuses
  'Draft': 'text-ink-gray-9',
  'Completed': 'text-green-900',
  'Rework': 'text-orange-800',
  
  // Sales Cycle specific
  'Quality Review': 'text-blue-800',
  
  // Procurement Cycle specific
  'Bucket': 'text-yellow-800',
  'Procurement Draft': 'text-ink-gray-9',
  'Procurement Review': 'text-purple-800',
  'Procurement Rework': 'text-orange-800',
  'Final Approved': 'text-green-800'
}

export const PRIORITY_COLORS = {
  'Low': 'bg-ink-gray-1',
  'Medium': 'bg-blue-50',
  'High': 'bg-orange-50',
  'Urgent': 'bg-red-50'
}
