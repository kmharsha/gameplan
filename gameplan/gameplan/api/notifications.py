from gameplan.gameplan.utils.simple_notifications import send_notification as send_simple_notification
"""
API methods for notifications
"""
import frappe
from frappe import _
import json


@frappe.whitelist()
def get_user_notifications(user=None, limit=50, unread_only=False):
	"""Get notifications for a user using GP Notification Log"""
	if not user:
		user = frappe.session.user

	# Use GP Notification Log system
	filters = {"recipient_user": user}
	if unread_only:
		filters["is_read"] = 0
	
	notifications = frappe.get_all(
		"GP Notification Log",
		filters=filters,
		fields=["name as id", "title", "body", "notification_type as type", "is_read", "read_at", "data", "creation as created_at"],
		order_by="creation desc",
		limit=limit
	)
	
	# Parse JSON data
	for notification in notifications:
		if notification.data:
			try:
				notification.data = json.loads(notification.data)
			except:
				notification.data = None
	
	return notifications


@frappe.whitelist()
def mark_notification_as_read(notification_id):
	"""Mark a specific notification as read"""
	notification = frappe.get_doc("GP Notification Log", notification_id)
	
	# Check permissions
	if notification.recipient_user != frappe.session.user:
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	
	notification.is_read = 1
	notification.read_at = frappe.utils.now()
	notification.save(ignore_permissions=True)
	return {"status": "success"}


@frappe.whitelist()
def mark_all_notifications_as_read():
	"""Mark all notifications as read for current user"""
	user = frappe.session.user
	
	# Mark notifications as read using GP Notification Log
	frappe.db.sql("""
		UPDATE `tabGP Notification Log` 
		SET is_read = 1, read_at = %s 
		WHERE recipient_user = %s AND is_read = 0
	""", (frappe.utils.now(), user))

	frappe.db.commit()
	return {"status": "success"}


@frappe.whitelist()
def get_unread_count():
	"""Get unread notification count for current user"""
	user = frappe.session.user
	
	# Count unread notifications using GP Notification Log
	count = frappe.db.count("GP Notification Log", {
		"recipient_user": user,
		"is_read": 0
	})

	return count


@frappe.whitelist()
def send_notification(title, body, notification_type="Custom", 
					 recipient_user=None, recipient_role=None,
					 reference_doctype=None, reference_name=None, data=None):
	"""Send a notification (admin/system use)"""
	# Check permissions - only system managers can send notifications
	if not frappe.has_permission("GP Notification Log", "create"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	
	# Parse data if it's a string
	if isinstance(data, str):
		import json
		try:
			data = json.loads(data)
		except:
			data = None
	
	return send_simple_notification(
		title=title,
		message=body,
		user=recipient_user,
		notification_type=notification_type,
		data=data
	)


@frappe.whitelist()
def send_custom_notification(title, body, recipient_user=None, recipient_role=None, data=None):
	"""Send a custom notification (admin/system use)"""
	return send_notification(
		title=title,
		body=body,
		notification_type="Custom",
		recipient_user=recipient_user,
		recipient_role=recipient_role,
		data=data
	)


@frappe.whitelist()
def send_system_notification(title, body, recipient_user=None, recipient_role=None, data=None):
	"""Send a system notification (admin/system use)"""
	return send_notification(
		title=title,
		body=body,
		notification_type="System",
		recipient_user=recipient_user,
		recipient_role=recipient_role,
		data=data
	)


@frappe.whitelist()
def test_notification():
	"""Test notification - sends a test notification to current user"""
	user = frappe.session.user
	
	notification = send_simple_notification(
		title="Test Notification",
		message="This is a test notification from Gameplan!",
		user=user,
		notification_type="System",
		data={"test": True, "timestamp": frappe.utils.now()}
	)
	
	return {
		"success": True,
		"message": "Test notification sent successfully!",
		"notification_id": notification.name
	}


@frappe.whitelist()
def send_task_status_change_notification(task_id, task_title, from_status, to_status, 
									   moved_by, project=None, customer=None, workflow_type=None):
	"""Send notification when task status changes"""
	title = f"Task Status Changed: {task_title}"
	body = f"Task '{task_title}' status changed from '{from_status}' to '{to_status}' by {moved_by}"
	
	data = {
		"task_id": task_id,
		"task_title": task_title,
		"from_status": from_status,
		"to_status": to_status,
		"moved_by": moved_by,
		"project": project,
		"customer": customer,
		"workflow_type": workflow_type
	}
	
	# Get task assignee to send notification to
	recipient_user = None
	try:
		task_doc = frappe.get_doc("GP Artwork Task", task_id)
		if task_doc.assigned_to and task_doc.assigned_to != moved_by:
			recipient_user = task_doc.assigned_to
	except:
		pass
	
	return send_simple_notification(
		title=title,
		message=body,
		user=recipient_user,
		notification_type="Task Status Change",
		data=data
	)


@frappe.whitelist()
def send_task_bucket_movement_notification(task_id, task_title, from_bucket, to_bucket,
										 moved_by, project=None, customer=None, workflow_type=None):
	"""Send notification when task is moved between buckets"""
	title = f"Task Moved: {task_title}"
	body = f"Task '{task_title}' moved from '{from_bucket}' to '{to_bucket}' by {moved_by}"
	
	data = {
		"task_id": task_id,
		"task_title": task_title,
		"from_bucket": from_bucket,
		"to_bucket": to_bucket,
		"moved_by": moved_by,
		"project": project,
		"customer": customer,
		"workflow_type": workflow_type
	}
	
	# Get task assignee to send notification to
	recipient_user = None
	try:
		task_doc = frappe.get_doc("GP Artwork Task", task_id)
		if task_doc.assigned_to and task_doc.assigned_to != moved_by:
			recipient_user = task_doc.assigned_to
	except:
		pass
	
	return send_simple_notification(
		title=title,
		message=body,
		user=recipient_user,
		notification_type="Task Movement",
		data=data
	)


@frappe.whitelist()
def send_task_assignment_notification(task_id, task_title, assigned_to, assigned_by,
									project=None, customer=None, workflow_type=None):
	"""Send notification when task is assigned"""
	title = f"New Task Assignment: {task_title}"
	body = f"Task '{task_title}' has been assigned to you by {assigned_by}"
	
	data = {
		"task_id": task_id,
		"task_title": task_title,
		"assigned_to": assigned_to,
		"assigned_by": assigned_by,
		"project": project,
		"customer": customer,
		"workflow_type": workflow_type
	}
	
	return send_simple_notification(
		title=title,
		message=body,
		user=assigned_to,
		notification_type="Task Assignment",
		data=data
	)


@frappe.whitelist()
def send_task_created_notification(task_id, task_title, created_by, assigned_to=None,
								 project=None, customer=None, workflow_type=None):
	"""Send notification when task is created"""
	title = f"New Task Created: {task_title}"
	body = f"New task '{task_title}' has been created by {created_by}"
	
	data = {
		"task_id": task_id,
		"task_title": task_title,
		"created_by": created_by,
		"assigned_to": assigned_to,
		"project": project,
		"customer": customer,
		"workflow_type": workflow_type
	}
	
	# Send to assignee if assigned
	recipient_user = assigned_to
	
	return send_simple_notification(
		title=title,
		message=body,
		user=recipient_user,
		notification_type="Task Assignment",
		data=data
	)


@frappe.whitelist()
def send_task_moved_to_sales_bucket_notification(task_id, task_title, moved_by,
											   project=None, customer=None):
	"""Send notification when task is moved to sales bucket"""
	title = f"Task Moved to Sales Bucket: {task_title}"
	body = f"Task '{task_title}' has been moved to the sales bucket by {moved_by}"
	
	data = {
		"task_id": task_id,
		"task_title": task_title,
		"moved_by": moved_by,
		"project": project,
		"customer": customer,
		"bucket": "Sales Bucket"
	}
	
	# Send to sales team
	return send_simple_notification(
		title=title,
		message=body,
		user=None,  # Will be handled by role-based distribution
		notification_type="Task Movement",
		data=data
	)


@frappe.whitelist()
def send_task_moved_from_procurement_bucket_notification(task_id, task_title, new_status,
													   moved_by, project=None, customer=None):
	"""Send notification when task is moved from procurement bucket"""
	title = f"Task Moved from Procurement Bucket: {task_title}"
	body = f"Task '{task_title}' has been moved from procurement bucket to '{new_status}' by {moved_by}"
	
	data = {
		"task_id": task_id,
		"task_title": task_title,
		"new_status": new_status,
		"moved_by": moved_by,
		"project": project,
		"customer": customer,
		"from_bucket": "Procurement Bucket"
	}
	
	# Send to procurement team
	return send_simple_notification(
		title=title,
		message=body,
		user=None,  # Will be handled by role-based distribution
		notification_type="Task Movement",
		data=data
	)
