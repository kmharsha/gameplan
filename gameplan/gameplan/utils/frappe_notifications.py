"""
Enhanced Frappe notification system with real-time WebSocket support
"""
import frappe
from frappe.utils import now
import json

def send_notification(title, message, user=None, reference_doctype=None, reference_name=None, data=None):
	"""
	Send notification using Frappe's built-in system with real-time WebSocket
	
	Args:
		title (str): Notification title
		message (str): Notification message
		user (str): User to send notification to
		reference_doctype (str): Related doctype
		reference_name (str): Related document name
		data (dict): Additional data
	"""
	
	# Create notification using Frappe's built-in system
	notification_data = {
		"doctype": "Notification",
		"subject": title,
		"type": "Mention",
		"email_content": message,
		"for_user": user or frappe.session.user,
		"read": 0
	}
	
	# Add reference fields only if provided
	if reference_doctype:
		notification_data["document_type"] = reference_doctype
	if reference_name:
		notification_data["document_name"] = reference_name
	
	notification = frappe.get_doc(notification_data)
	
	notification.insert(ignore_permissions=True)
	
	# Publish real-time notification via WebSocket
	notification_data = {
		"id": notification.name,
		"title": title,
		"body": message,
		"type": "Mention",
		"reference_doctype": reference_doctype,
		"reference_name": reference_name,
		"data": data,
		"created_at": notification.creation,
		"is_read": False
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
		reference_doctype="GP Artwork Task",
		reference_name=task_id,
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
		reference_doctype="GP Artwork Task",
		reference_name=task_id,
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
		reference_doctype="GP Artwork Task",
		reference_name=task_id,
		data=data
	)
