# Copyright (c) 2025, Frappe Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def notify_artwork_task_update(task_name, event_type, data=None):
	"""Send real-time notifications for artwork task updates"""
	try:
		task = frappe.get_doc("GP Artwork Task", task_name)
		
		# Determine who should receive the notification
		users_to_notify = []
		
		if event_type == "status_changed":
			# Get users based on new status
			notification_map = {
				"Awaiting Quality Review": get_users_with_role("Artwork Quality Team"),
				"Rework": [task.created_by_sales],
				"Approved by Quality": get_users_with_role("Artwork Procurement Team"),
				"Awaiting Final Review": get_users_with_role("Artwork Quality Team"),
				"Final Rework": get_users_with_role("Artwork Procurement Team"),
				"Final Approved": get_all_artwork_users()
			}
			
			users_to_notify = notification_map.get(data.get("new_status", ""), [])
			
		elif event_type == "comment_added":
			# Notify all users who have participated in the task
			users_to_notify = get_task_participants(task_name)
			
		elif event_type == "attachment_added":
			# Notify all users who have participated in the task
			users_to_notify = get_task_participants(task_name)
		
		# Send real-time updates via Socket.io
		for user in users_to_notify:
			if user != frappe.session.user:  # Don't notify the user who made the change
				frappe.publish_realtime(
					event="artwork_task_update",
					message={
						"task_name": task_name,
						"task_title": task.title,
						"event_type": event_type,
						"data": data or {}
					},
					user=user,
					doctype="GP Artwork Task",
					docname=task_name
				)
				
	except Exception as e:
		frappe.log_error(f"Error in artwork task real-time notification: {str(e)}")


def get_users_with_role(role):
	"""Get all users with a specific role"""
	return [
		d.parent for d in frappe.get_all(
			"Has Role",
			filters={"role": role, "parenttype": "User"},
			fields=["parent"]
		)
	]


def get_all_artwork_users():
	"""Get all users with artwork-related roles"""
	users = []
	for role in ["Artwork Sales Team", "Artwork Quality Team", "Artwork Procurement Team"]:
		users.extend(get_users_with_role(role))
	return list(set(users))


def get_task_participants(task_name):
	"""Get all users who have participated in a task"""
	participants = set()
	
	# Get task owner
	task = frappe.get_doc("GP Artwork Task", task_name)
	participants.add(task.created_by_sales)
	if task.assigned_to:
		participants.add(task.assigned_to)
	
	# Get users who commented
	commenters = frappe.get_all(
		"GP Comment",
		filters={"reference_doctype": "GP Artwork Task", "reference_name": task_name},
		pluck="owner"
	)
	participants.update(commenters)
	
	# Get users who changed status
	status_changers = [h.changed_by for h in task.status_history if h.changed_by]
	participants.update(status_changers)
	
	return list(participants)


@frappe.whitelist()
def get_artwork_task_updates(last_update=None):
	"""Get recent artwork task updates for real-time polling fallback"""
	filters = {}
	
	if last_update:
		filters["modified"] = (">", last_update)
	
	tasks = frappe.get_all(
		"GP Artwork Task",
		filters=filters,
		fields=["name", "title", "status", "modified"],
		order_by="modified desc",
		limit=50
	)
	
	return {
		"tasks": tasks,
		"timestamp": frappe.utils.now()
	}
