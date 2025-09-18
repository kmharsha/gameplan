import frappe
from frappe.model.document import Document
from frappe.utils import now, get_datetime
from gameplan.gameplan.utils.notifications import NotificationManager
import json


class GPNotificationSender(Document):
	def before_save(self):
		if not self.created_at:
			self.created_at = now()
		if not self.created_by:
			self.created_by = frappe.session.user

	def after_insert(self):
		if self.send_immediately:
			self.send_notification()

	def send_notification(self):
		"""Send the notification"""
		try:
			# Parse data if it's a string
			data = None
			if self.data:
				try:
					data = json.loads(self.data) if isinstance(self.data, str) else self.data
				except:
					data = None

			# Send notification
			notification = NotificationManager.send_notification(
				title=self.title,
				body=self.body,
				notification_type=self.notification_type,
				recipient_user=self.recipient_user,
				recipient_role=self.recipient_role,
				reference_doctype=self.reference_doctype,
				reference_name=self.reference_name,
				data=data,
				publish_realtime=True
			)

			# Update status
			self.status = "Sent"
			self.sent_at = now()
			self.save(ignore_permissions=True)

			frappe.msgprint(f"Notification sent successfully to {self.get_recipient_display()}")
			return notification

		except Exception as e:
			self.status = "Failed"
			self.save(ignore_permissions=True)
			frappe.throw(f"Failed to send notification: {str(e)}")

	def get_recipient_display(self):
		"""Get display text for recipient"""
		if self.recipient_user:
			return f"User: {self.recipient_user}"
		elif self.recipient_role:
			return f"Role: {self.recipient_role}"
		else:
			return "All users"

	def schedule_notification(self):
		"""Schedule notification for later sending"""
		if not self.scheduled_time:
			frappe.throw("Scheduled time is required for scheduling notifications")

		if get_datetime(self.scheduled_time) <= get_datetime(now()):
			frappe.throw("Scheduled time must be in the future")

		self.status = "Scheduled"
		self.save(ignore_permissions=True)
		frappe.msgprint(f"Notification scheduled for {self.scheduled_time}")

	@staticmethod
	def send_quick_notification(title, body, notification_type="Custom", 
							   recipient_user=None, recipient_role=None,
							   reference_doctype=None, reference_name=None, 
							   data=None):
		"""Quick method to send a notification"""
		sender = frappe.get_doc({
			"doctype": "GP Notification Sender",
			"title": title,
			"body": body,
			"notification_type": notification_type,
			"recipient_user": recipient_user,
			"recipient_role": recipient_role,
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
			"data": json.dumps(data) if data else None,
			"send_immediately": 1
		})
		
		sender.insert(ignore_permissions=True)
		return sender

	@staticmethod
	def send_bulk_notification(title, body, notification_type="Custom", 
							  recipient_users=None, recipient_roles=None,
							  reference_doctype=None, reference_name=None, 
							  data=None):
		"""Send notification to multiple users/roles"""
		notifications_sent = 0
		
		# Send to individual users
		if recipient_users:
			for user in recipient_users:
				GPNotificationSender.send_quick_notification(
					title=title,
					body=body,
					notification_type=notification_type,
					recipient_user=user,
					reference_doctype=reference_doctype,
					reference_name=reference_name,
					data=data
				)
				notifications_sent += 1

		# Send to roles
		if recipient_roles:
			for role in recipient_roles:
				GPNotificationSender.send_quick_notification(
					title=title,
					body=body,
					notification_type=notification_type,
					recipient_role=role,
					reference_doctype=reference_doctype,
					reference_name=reference_name,
					data=data
				)
				notifications_sent += 1

		return notifications_sent

	@staticmethod
	def get_notification_stats():
		"""Get notification statistics"""
		stats = frappe.db.sql("""
			SELECT 
				status,
				COUNT(*) as count
			FROM `tabGP Notification Sender`
			WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
			GROUP BY status
		""", as_dict=True)

		return {stat.status: stat.count for stat in stats}

	@staticmethod
	def cleanup_old_notifications(days=30):
		"""Clean up old sent notifications"""
		frappe.db.sql("""
			DELETE FROM `tabGP Notification Sender`
			WHERE status = 'Sent' 
			AND sent_at < DATE_SUB(NOW(), INTERVAL %s DAY)
		""", (days,))
		
		frappe.db.commit()
		return "Old notifications cleaned up successfully"
