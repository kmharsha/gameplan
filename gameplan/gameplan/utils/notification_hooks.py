"""
Notification hooks for document events
"""
import frappe
from frappe.utils import now
from .notifications import NotificationManager


def send_task_notifications(doc, method):
	"""Send notifications for GP Task events"""
	if method == "after_insert":
		# New task created
		if doc.assigned_to:
			NotificationManager.send_task_assignment_notification(doc, doc.assigned_to)
	
	elif method == "on_update":
		# Task updated - check for status changes
		old_doc = doc.get_doc_before_save()
		if old_doc and old_doc.status != doc.status:
			NotificationManager.send_task_status_change_notification(
				doc, old_doc.status, doc.status, frappe.session.user
			)
		
		# Check for assignment changes
		if old_doc and old_doc.assigned_to != doc.assigned_to and doc.assigned_to:
			NotificationManager.send_task_assignment_notification(doc, doc.assigned_to)


def send_artwork_task_notifications(doc, method):
	"""Send notifications for GP Artwork Task events"""
	if method == "after_insert":
		# New artwork task created
		if doc.assigned_to:
			title = f"New Artwork Task: {doc.title}"
			body = f"Artwork task '{doc.title}' has been assigned to you"
			
			data = {
				"task_id": doc.name,
				"task_title": doc.title,
				"artwork": doc.artwork,
				"customer": doc.customer,
				"workflow_type": doc.workflow_type,
				"status": doc.status,
				"priority": doc.priority
			}
			
			NotificationManager.send_notification(
				title=title,
				body=body,
				notification_type="Task Assignment",
				recipient_user=doc.assigned_to,
				reference_doctype="GP Artwork Task",
				reference_name=doc.name,
				data=data
			)
	
	elif method == "on_update":
		# Artwork task updated - check for status changes
		old_doc = doc.get_doc_before_save()
		if old_doc and old_doc.status != doc.status:
			title = f"Artwork Task Status Changed: {doc.title}"
			body = f"Artwork task '{doc.title}' status changed from '{old_doc.status}' to '{doc.status}' by {frappe.session.user}"
			
			data = {
				"task_id": doc.name,
				"task_title": doc.title,
				"old_status": old_doc.status,
				"new_status": doc.status,
				"changed_by": frappe.session.user,
				"artwork": doc.artwork,
				"customer": doc.customer
			}
			
			# Send to task assignee if different from who changed it
			recipient_user = None
			if doc.assigned_to and doc.assigned_to != frappe.session.user:
				recipient_user = doc.assigned_to
			
			# Only send notification if there's a valid recipient
			if recipient_user:
				NotificationManager.send_notification(
					title=title,
					body=body,
					notification_type="Task Status Change",
					recipient_user=recipient_user,
					reference_doctype="GP Artwork Task",
					reference_name=doc.name,
					data=data
				)
		
		# Check for assignment changes
		if old_doc and old_doc.assigned_to != doc.assigned_to and doc.assigned_to:
			title = f"New Artwork Task Assignment: {doc.title}"
			body = f"Artwork task '{doc.title}' has been assigned to you"
			
			data = {
				"task_id": doc.name,
				"task_title": doc.title,
				"artwork": doc.artwork,
				"customer": doc.customer,
				"workflow_type": doc.workflow_type,
				"status": doc.status,
				"priority": doc.priority
			}
			
			NotificationManager.send_notification(
				title=title,
				body=body,
				notification_type="Task Assignment",
				recipient_user=doc.assigned_to,
				reference_doctype="GP Artwork Task",
				reference_name=doc.name,
				data=data
			)


def send_project_notifications(doc, method):
	"""Send notifications for GP Project events"""
	if method == "after_insert":
		# New project created
		NotificationManager.send_project_update_notification(doc, "created", frappe.session.user)
	
	elif method == "on_update":
		# Project updated
		old_doc = doc.get_doc_before_save()
		if old_doc:
			# Check for title changes
			if old_doc.title != doc.title:
				NotificationManager.send_project_update_notification(doc, "renamed", frappe.session.user)
			# Check for description changes
			elif old_doc.description != doc.description:
				NotificationManager.send_project_update_notification(doc, "updated", frappe.session.user)
			# Check for member changes
			elif old_doc.members != doc.members:
				NotificationManager.send_project_update_notification(doc, "members updated", frappe.session.user)


def send_task_movement_notification(task_doc, from_bucket, to_bucket):
	"""Send notification when task is moved between buckets"""
	NotificationManager.send_task_movement_notification(
		task_doc, from_bucket, to_bucket, frappe.session.user
	)
