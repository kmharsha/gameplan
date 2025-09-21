/**
 * Task movement notification utilities
 */
import { apiCall } from '@/utils/api'

export interface TaskMovementData {
  taskId: string
  taskTitle: string
  fromStatus: string
  toStatus: string
  fromBucket?: string
  toBucket?: string
  movedBy: string
  project?: string
  customer?: string
  workflowType?: string
}

/**
 * Send notification when task is moved between statuses
 */
export async function sendTaskStatusChangeNotification(data: TaskMovementData) {
  try {
    await apiCall('gameplan.gameplan.api.notifications.send_task_status_change_notification', {
        task_id: data.taskId,
        task_title: data.taskTitle,
        from_status: data.fromStatus,
        to_status: data.toStatus,
        moved_by: data.movedBy,
        project: data.project,
        customer: data.customer,
        workflow_type: data.workflowType
      })
  } catch (error) {
    console.error('Error sending task status change notification:', error)
  }
}

/**
 * Send notification when task is moved to/from buckets
 */
export async function sendTaskBucketMovementNotification(data: TaskMovementData) {
  try {
    await apiCall('gameplan.gameplan.api.notifications.send_task_bucket_movement_notification', {
        task_id: data.taskId,
        task_title: data.taskTitle,
        from_bucket: data.fromBucket,
        to_bucket: data.toBucket,
        moved_by: data.movedBy,
        project: data.project,
        customer: data.customer,
        workflow_type: data.workflowType
      })
  } catch (error) {
    console.error('Error sending task bucket movement notification:', error)
  }
}

/**
 * Send notification when task is assigned
 */
export async function sendTaskAssignmentNotification(data: {
  taskId: string
  taskTitle: string
  assignedTo: string
  assignedBy: string
  project?: string
  customer?: string
  workflowType?: string
}) {
  try {
    await apiCall('gameplan.gameplan.api.notifications.send_task_assignment_notification', {
        task_id: data.taskId,
        task_title: data.taskTitle,
        assigned_to: data.assignedTo,
        assigned_by: data.assignedBy,
        project: data.project,
        customer: data.customer,
        workflow_type: data.workflowType
      })
  } catch (error) {
    console.error('Error sending task assignment notification:', error)
  }
}

/**
 * Send notification when task is created
 */
export async function sendTaskCreatedNotification(data: {
  taskId: string
  taskTitle: string
  createdBy: string
  assignedTo?: string
  project?: string
  customer?: string
  workflowType?: string
}) {
  try {
    await apiCall('gameplan.gameplan.api.notifications.send_task_created_notification', {
        task_id: data.taskId,
        task_title: data.taskTitle,
        created_by: data.createdBy,
        assigned_to: data.assignedTo,
        project: data.project,
        customer: data.customer,
        workflow_type: data.workflowType
      })
  } catch (error) {
    console.error('Error sending task created notification:', error)
  }
}

/**
 * Send notification when task is moved to sales bucket
 */
export async function sendTaskMovedToSalesBucketNotification(data: {
  taskId: string
  taskTitle: string
  movedBy: string
  project?: string
  customer?: string
}) {
  try {
    await apiCall('gameplan.gameplan.api.notifications.send_task_moved_to_sales_bucket_notification', {
        task_id: data.taskId,
        task_title: data.taskTitle,
        moved_by: data.movedBy,
        project: data.project,
        customer: data.customer
      })
  } catch (error) {
    console.error('Error sending task moved to sales bucket notification:', error)
  }
}

/**
 * Send notification when task is moved from procurement bucket
 */
export async function sendTaskMovedFromProcurementBucketNotification(data: {
  taskId: string
  taskTitle: string
  newStatus: string
  movedBy: string
  project?: string
  customer?: string
}) {
  try {
    await apiCall('gameplan.gameplan.api.notifications.send_task_moved_from_procurement_bucket_notification', {
        task_id: data.taskId,
        task_title: data.taskTitle,
        new_status: data.newStatus,
        moved_by: data.movedBy,
        project: data.project,
        customer: data.customer
      })
  } catch (error) {
    console.error('Error sending task moved from procurement bucket notification:', error)
  }
}
