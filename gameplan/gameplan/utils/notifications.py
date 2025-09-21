"""
Notification utilities for Gameplan
"""
import frappe
from frappe.utils import now
import json


class NotificationManager:
	"""Manager class for handling notifications"""
	
	@staticmethod
	def send_notification(title, body, notification_type="Custom", 
						 recipient_user=None, recipient_role=None,
						 reference_doctype=None, reference_name=None, 
						 data=None, publish_realtime=True):
		"""
		Send a notification to users
		
		Args:
			title (str): Notification title
			body (str): Notification body/message
			notification_type (str): Type of notification
			recipient_user (str): Specific user to send to
			recipient_role (str): Role to send to all users with this role
			reference_doctype (str): Related doctype
			reference_name (str): Related document name
			data (dict): Additional data
			publish_realtime (bool): Whether to publish real-time event
		"""
		# Don't create notification if no recipient is specified
		if not recipient_user and not recipient_role:
			return None
			
		# Create notification log
		notification = frappe.get_doc({
			"doctype": "GP Notification Log",
			"title": title,
			"body": body,
			"notification_type": notification_type,
			"recipient_user": recipient_user,
			"recipient_role": recipient_role,
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
			"data": json.dumps(data) if data else None
		})
		
		notification.insert(ignore_permissions=True)
		
		if publish_realtime:
			NotificationManager.publish_realtime_notification(notification)
		
		return notification

	@staticmethod
	def publish_realtime_notification(notification):
		"""Publish real-time notification event"""
		notification_data = {
			"title": notification.title,
			"body": notification.body,
			"notification_type": notification.notification_type,
			"reference_doctype": notification.reference_doctype,
			"reference_name": notification.reference_name,
			"data": notification.data,
			"created_at": notification.created_at,
			"id": notification.name
		}

		# Send to specific user if recipient_user is set
		if notification.recipient_user:
			frappe.publish_realtime(
				"new_notification",
				notification_data,
				user=notification.recipient_user
			)
		# Send to all users with specific role if recipient_role is set
		elif notification.recipient_role:
			users = frappe.get_all("Has Role", 
				filters={"role": notification.recipient_role, "parenttype": "User"},
				fields=["parent"]
			)
			for user in users:
				frappe.publish_realtime(
					"new_notification",
					notification_data,
					user=user.parent
				)
		# Send to all users if no specific recipient
		else:
			frappe.publish_realtime("new_notification", notification_data)

	@staticmethod
	def send_task_assignment_notification(task_doc, assigned_to):
		"""Send notification when task is assigned"""
		title = f"New Task Assigned: {task_doc.title}"
		body = f"Task '{task_doc.title}' has been assigned to you"
		
		data = {
			"task_id": task_doc.name,
			"task_title": task_doc.title,
			"project": task_doc.project,
			"priority": task_doc.priority,
			"due_date": task_doc.due_date
		}
		
		return NotificationManager.send_notification(
			title=title,
			body=body,
			notification_type="Task Assignment",
			recipient_user=assigned_to,
			reference_doctype="GP Task",
			reference_name=task_doc.name,
			data=data
		)

	@staticmethod
	def send_task_status_change_notification(task_doc, old_status, new_status, changed_by):
		"""Send notification when task status changes"""
		title = f"Task Status Changed: {task_doc.title}"
		body = f"Task '{task_doc.title}' status changed from '{old_status}' to '{new_status}' by {changed_by}"
		
		data = {
			"task_id": task_doc.name,
			"task_title": task_doc.title,
			"old_status": old_status,
			"new_status": new_status,
			"changed_by": changed_by,
			"project": task_doc.project
		}
		
		# Send to task assignee if different from who changed it
		recipient_user = None
		if task_doc.assigned_to and task_doc.assigned_to != changed_by:
			recipient_user = task_doc.assigned_to
		
		# Only send notification if there's a valid recipient
		if recipient_user:
			return NotificationManager.send_notification(
				title=title,
				body=body,
				notification_type="Task Status Change",
				recipient_user=recipient_user,
				reference_doctype="GP Task",
				reference_name=task_doc.name,
				data=data
			)
		return None

	@staticmethod
	def send_task_movement_notification(task_doc, from_bucket, to_bucket, moved_by):
		"""Send notification when task is moved between buckets"""
		title = f"Task Moved: {task_doc.title}"
		body = f"Task '{task_doc.title}' moved from '{from_bucket}' to '{to_bucket}' by {moved_by}"
		
		data = {
			"task_id": task_doc.name,
			"task_title": task_doc.title,
			"from_bucket": from_bucket,
			"to_bucket": to_bucket,
			"moved_by": moved_by,
			"project": task_doc.project
		}
		
		# Send to task assignee if different from who moved it
		recipient_user = None
		if task_doc.assigned_to and task_doc.assigned_to != moved_by:
			recipient_user = task_doc.assigned_to
		
		# Only send notification if there's a valid recipient
		if recipient_user:
			return NotificationManager.send_notification(
				title=title,
				body=body,
				notification_type="Task Movement",
				recipient_user=recipient_user,
				reference_doctype="GP Task",
				reference_name=task_doc.name,
				data=data
			)
		return None

	@staticmethod
	def send_project_update_notification(project_doc, update_type, updated_by):
		"""Send notification for project updates"""
		title = f"Project Updated: {project_doc.title}"
		body = f"Project '{project_doc.title}' has been {update_type} by {updated_by}"
		
		data = {
			"project_id": project_doc.name,
			"project_title": project_doc.title,
			"update_type": update_type,
			"updated_by": updated_by
		}
		
		# Send to all project members
		recipient_role = None
		if project_doc.members:
			# Get all project members
			member_emails = [member.user for member in project_doc.members]
			for member_email in member_emails:
				NotificationManager.send_notification(
					title=title,
					body=body,
					notification_type="Project Update",
					recipient_user=member_email,
					reference_doctype="GP Project",
					reference_name=project_doc.name,
					data=data
				)
		else:
			# Send to all users if no specific members
			NotificationManager.send_notification(
				title=title,
				body=body,
				notification_type="Project Update",
				reference_doctype="GP Project",
				reference_name=project_doc.name,
				data=data
			)

	@staticmethod
	def send_custom_notification(title, body, recipient_user=None, recipient_role=None, data=None):
		"""Send a custom notification"""
		return NotificationManager.send_notification(
			title=title,
			body=body,
			notification_type="Custom",
			recipient_user=recipient_user,
			recipient_role=recipient_role,
			data=data
		)

	@staticmethod
	def send_system_notification(title, body, recipient_user=None, recipient_role=None, data=None):
		"""Send a system notification"""
		return NotificationManager.send_notification(
			title=title,
			body=body,
			notification_type="System",
			recipient_user=recipient_user,
			recipient_role=recipient_role,
			data=data
		)
