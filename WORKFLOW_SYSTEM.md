# Workflow System Documentation

## Overview

The Gameplan Workflow System implements a two-cycle workflow for artwork tasks: **Sales Cycle** and **Procurement Cycle**. This system ensures proper handoff between teams and maintains task visibility based on user roles.

## Workflow Cycles

### Sales Cycle
**Flow:** Draft → Quality Review → Rework → Completed

- **Draft**: Initial task creation by Sales team
- **Quality Review**: Quality team reviews the task
- **Rework**: Task sent back to Sales for modifications
- **Completed**: Task approved and ready for Procurement

### Procurement Cycle
**Flow:** Bucket → Draft → Procurement Review → Quality Review → Rework → Final Approved

- **Bucket**: Holding place for completed Sales tasks
- **Draft**: New Procurement task created from Bucket
- **Procurement Review**: Procurement team reviews the task
- **Quality Review**: Quality team reviews Procurement task
- **Rework**: Task sent back for modifications
- **Final Approved**: Task fully approved and completed

## Key Features

### 1. Automatic Task Handoff
When a Sales Cycle task reaches "Completed" status, it automatically:
- Changes workflow type to "Procurement Cycle"
- Changes status to "Bucket"
- Increments cycle count
- Becomes visible to Procurement team

### 2. Role-Based Visibility
- **Sales Role**: Can only see Sales Cycle tasks
- **Procurement Role**: Can only see Procurement Cycle tasks (including Bucket)
- **Quality Role**: Can see both cycles
- **System Manager/Gameplan Admin**: Full access to all tasks

### 3. Procurement Bucket
The Bucket serves as a holding place where:
- Completed Sales tasks are automatically placed
- Procurement team can pick up tasks to start Procurement Cycle
- Tasks can be filtered and sorted by various criteria
- Cycle count tracking shows how many times a task has cycled

## API Endpoints

### Core Workflow APIs
- `get_artwork_kanban_data()`: Get tasks organized by status for Kanban view
- `get_bucket_tasks()`: Get all tasks in Bucket status
- `move_task_from_bucket()`: Move task from Bucket to active workflow
- `get_workflow_summary()`: Get summary statistics for both cycles
- `get_workflow_tasks()`: Get tasks filtered by workflow type and role

### Task Management APIs
- `create_artwork_task()`: Create new task with specified workflow type
- `update_artwork_task_status()`: Update task status with validation
- `get_artwork_task_transitions()`: Get allowed status transitions for current user
- `get_artwork_task_details()`: Get detailed task information with comments

## Frontend Components

### Pages
- **ArtworkKanban.vue**: Main Kanban board for both workflows
- **ProcurementBucket.vue**: Dedicated page for Procurement Bucket
- **ArtworkTask.vue**: Individual task detail page

### Components
- **BucketTaskCard.vue**: Card component for tasks in Bucket
- **KanbanColumn.vue**: Column component for Kanban board
- **StatusChangeDialog.vue**: Dialog for status transitions

## Database Schema

### GP Artwork Task Fields
- `workflow_type`: "Sales Cycle" or "Procurement Cycle"
- `status`: Current status in the workflow
- `cycle_count`: Number of times task has cycled from Sales to Procurement
- `sales_cycle_reference`: Link to original Sales task (for Procurement tasks)
- `last_status_change`: Timestamp of last status change
- `last_status_changed_by`: User who made last status change

### Status History
All status changes are tracked in the `status_history` child table with:
- `from_status`: Previous status
- `to_status`: New status
- `changed_by`: User who made the change
- `change_date`: Timestamp of change
- `reason`: Reason for change
- `comments`: Additional comments

## Role Permissions

### Sales Role
- **Create**: Sales Cycle tasks only
- **Read**: Sales Cycle tasks only
- **Write**: Sales Cycle tasks in Draft or Rework status
- **Status Transitions**: Draft → Quality Review, Rework → Quality Review

### Procurement Role
- **Create**: Procurement Cycle tasks only
- **Read**: Procurement Cycle tasks only (including Bucket)
- **Write**: Procurement Cycle tasks in Draft, Procurement Review, or Rework status
- **Status Transitions**: Bucket → Procurement Review, Draft → Procurement Review, Procurement Review → Quality Review, Rework → Procurement Review

### Quality Role
- **Create**: Both workflow types
- **Read**: Both workflow types
- **Write**: Tasks in Quality Review, Rework, or Final Approved status
- **Status Transitions**: Quality Review → Completed/Rework, Quality Review → Final Approved/Rework

## Usage Examples

### Creating a Sales Task
```python
task = frappe.new_doc("GP Artwork Task")
task.title = "Logo Design for Client ABC"
task.artwork = "ART-001"
task.workflow_type = "Sales Cycle"
task.status = "Draft"
task.description = "Create a new logo design"
task.priority = "High"
task.insert()
```

### Moving Task Through Sales Cycle
```python
# Sales moves to Quality Review
task.status = "Quality Review"
task.save()

# Quality approves (moves to Completed)
task.status = "Completed"
task.save()
# Task automatically moves to Bucket
```

### Picking Up from Bucket
```python
# Procurement picks up from Bucket
task.status = "Procurement Review"
task.save()
```

### Creating Procurement Task from Bucket
```python
procurement_task = frappe.new_doc("GP Artwork Task")
procurement_task.title = "Vendor Selection for Logo Production"
procurement_task.artwork = "ART-001"
procurement_task.workflow_type = "Procurement Cycle"
procurement_task.status = "Draft"
procurement_task.sales_cycle_reference = sales_task.name
procurement_task.cycle_count = sales_task.cycle_count
procurement_task.insert()
```

## Configuration

### Status Colors
- **Draft**: Gray
- **Quality Review**: Blue
- **Rework**: Orange
- **Completed**: Green
- **Procurement Review**: Purple
- **Final Approved**: Green
- **Bucket**: Orange

### Priority Levels
- **Low**: Gray
- **Medium**: Blue
- **High**: Orange
- **Urgent**: Red

## Testing

Run the test script to verify the workflow system:
```bash
python test_workflow_system.py
```

This will test:
1. Sales Cycle workflow
2. Automatic task handoff to Bucket
3. Procurement Cycle workflow
4. Role-based permissions
5. API endpoints

## Troubleshooting

### Common Issues
1. **Task not moving to Bucket**: Check if Sales task is in "Completed" status
2. **Permission denied**: Verify user has correct role assigned
3. **Status transition not allowed**: Check user role and current status
4. **API errors**: Verify all required fields are provided

### Debug Steps
1. Check task workflow_type and status
2. Verify user roles and permissions
3. Check status history for transition errors
4. Review API logs for detailed error messages

## Future Enhancements

1. **Email Notifications**: Send emails on status changes
2. **SLA Tracking**: Track time spent in each status
3. **Bulk Operations**: Allow bulk status changes
4. **Advanced Filtering**: More filter options for tasks
5. **Reporting**: Detailed reports on workflow performance
6. **Mobile Support**: Mobile-optimized interface
7. **Integration**: Connect with external systems
8. **Automation**: Automated status transitions based on conditions