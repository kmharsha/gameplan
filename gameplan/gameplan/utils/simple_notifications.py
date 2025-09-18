"""
Simple notification system using GP Notification Log with real-time WebSocket support
"""
import frappe
from frappe.utils import now
import json

def send_notification(title, message, user=None, notification_type="System", data=None):
	"""
	Send notification using GP Notification Log with real-time WebSocket
	
	Args:
		title (str): Notification title
		message (str): Notification message
		user (str): User to send notification to
		notification_type (str): Type of notification
		data (dict): Additional data
	"""
	
	# Create notification using GP Notification Log
	notification = frappe.get_doc({
		"doctype": "GP Notification Log",
		"title": title,
		"body": message,
		"notification_type": notification_type,
		"recipient_user": user or frappe.session.user,
		"is_read": 0
	})
	
	# Add data if provided
	if data:
		notification.data = json.dumps(data)
	
	notification.insert(ignore_permissions=True)
	
	# Publish real-time notification via WebSocket
	notification_data = {
		"id": notification.name,
		"title": title,
		"body": message,
		"type": notification_type,
		"is_read": False,
		"data": data,
		"created_at": str(notification.creation)
	}
	
	# Send real-time notification
	frappe.publish_realtime(
		"new_notification",
		notification_data,
		user=user or frappe.session.user
	)
	
	return notification

def send_task_notification(task_title, action, user=None, task_id=None, project=None):
	"""Send task-related notification"""
	title = f"Task {action}: {task_title}"
	message = f"Task '{task_title}' has been {action}"
	
	data = {
		"task_id": task_id,
		"task_title": task_title,
		"action": action,
		"project": project
	}
	
	return send_notification(
		title=title,
		message=message,
		user=user,
		notification_type="Task Assignment",
		data=data
	)

def send_task_movement_notification(task_title, from_status, to_status, user=None, task_id=None):
	"""Send task movement notification"""
	title = f"Task Moved: {task_title}"
	message = f"Task '{task_title}' moved from '{from_status}' to '{to_status}'"
	
	data = {
		"task_id": task_id,
		"task_title": task_title,
		"from_status": from_status,
		"to_status": to_status,
		"moved_by": frappe.session.user
	}
	
	return send_notification(
		title=title,
		message=message,
		user=user,
		notification_type="Task Movement",
		data=data
	)

def send_bucket_movement_notification(task_title, bucket_name, user=None, task_id=None):
	"""Send bucket movement notification"""
	title = f"Task Moved to {bucket_name}: {task_title}"
	message = f"Task '{task_title}' has been moved to {bucket_name}"
	
	data = {
		"task_id": task_id,
		"task_title": task_title,
		"bucket": bucket_name,
		"moved_by": frappe.session.user
	}
	
	return send_notification(
		title=title,
		message=message,
		user=user,
		notification_type="Task Movement",
		data=data
	)
