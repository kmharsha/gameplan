import frappe
from frappe.model.document import Document
from frappe.utils import now, get_datetime
import json


class GPNotificationLog(Document):
	def before_save(self):
		if not self.created_at:
			self.created_at = now()
		if not self.created_by:
			self.created_by = frappe.session.user

	def after_insert(self):
		# Publish real-time notification
		self.publish_notification()

	def publish_notification(self):
		"""Publish notification to real-time subscribers"""
		notification_data = {
			"title": self.title,
			"body": self.body,
			"notification_type": self.notification_type,
			"reference_doctype": self.reference_doctype,
			"reference_name": self.reference_name,
			"data": self.data,
			"created_at": self.created_at,
			"id": self.name
		}

		# Send to specific user if recipient_user is set
		if self.recipient_user:
			frappe.publish_realtime(
				"new_notification",
				notification_data,
				user=self.recipient_user
			)
		# Send to all users with specific role if recipient_role is set
		elif self.recipient_role:
			users = frappe.get_all("Has Role", 
				filters={"role": self.recipient_role, "parenttype": "User"},
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

	def mark_as_read(self):
		"""Mark notification as read"""
		self.is_read = 1
		self.read_at = now()
		self.save(ignore_permissions=True)

	@staticmethod
	def create_notification(title, body, notification_type="Custom", 
						   recipient_user=None, recipient_role=None,
						   reference_doctype=None, reference_name=None, 
						   data=None):
		"""Create a new notification"""
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
		return notification

	@staticmethod
	def get_user_notifications(user=None, limit=50, unread_only=False):
		"""Get notifications for a user"""
		if not user:
			user = frappe.session.user

		filters = {
			"recipient_user": user
		}
		
		if unread_only:
			filters["is_read"] = 0

		notifications = frappe.get_all(
			"GP Notification Log",
			filters=filters,
			fields=["*"],
			order_by="created_at desc",
			limit=limit
		)

		# Also get role-based notifications
		user_roles = frappe.get_roles(user)
		role_filters = {
			"recipient_role": ["in", user_roles],
			"recipient_user": ["is", "not set"]
		}
		
		if unread_only:
			role_filters["is_read"] = 0

		role_notifications = frappe.get_all(
			"GP Notification Log",
			filters=role_filters,
			fields=["*"],
			order_by="created_at desc",
			limit=limit
		)

		# Combine and sort notifications
		all_notifications = notifications + role_notifications
		all_notifications.sort(key=lambda x: x.created_at, reverse=True)
		
		return all_notifications[:limit]

	@staticmethod
	def mark_all_as_read(user=None):
		"""Mark all notifications as read for a user"""
		if not user:
			user = frappe.session.user

		# Mark user-specific notifications as read
		frappe.db.sql("""
			UPDATE `tabGP Notification Log` 
			SET is_read = 1, read_at = %s 
			WHERE recipient_user = %s AND is_read = 0
		""", (now(), user))

		# Mark role-based notifications as read
		user_roles = frappe.get_roles(user)
		frappe.db.sql("""
			UPDATE `tabGP Notification Log` 
			SET is_read = 1, read_at = %s 
			WHERE recipient_role IN %s 
			AND recipient_user IS NULL 
			AND is_read = 0
		""", (now(), user_roles))

		frappe.db.commit()

	@staticmethod
	def get_unread_count(user=None):
		"""Get unread notification count for a user"""
		if not user:
			user = frappe.session.user

		# Count user-specific notifications
		user_count = frappe.db.count("GP Notification Log", {
			"recipient_user": user,
			"is_read": 0
		})

		# Count role-based notifications
		user_roles = frappe.get_roles(user)
		role_count = frappe.db.count("GP Notification Log", {
			"recipient_role": ["in", user_roles],
			"recipient_user": ["is", "not set"],
			"is_read": 0
		})

		return user_count + role_count
