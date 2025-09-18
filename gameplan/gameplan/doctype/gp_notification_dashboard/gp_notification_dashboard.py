import frappe
from frappe.model.document import Document
from frappe.utils import now
import json


class GPNotificationDashboard(Document):
	def before_save(self):
		if not self.created_at:
			self.created_at = now()
		if not self.created_by:
			self.created_by = frappe.session.user

	def after_insert(self):
		self.refresh_dashboard_data()

	def refresh_dashboard_data(self):
		"""Refresh dashboard data"""
		data = {
			"total_notifications": self.get_total_notifications(),
			"notifications_by_type": self.get_notifications_by_type(),
			"notifications_by_status": self.get_notifications_by_status(),
			"recent_notifications": self.get_recent_notifications(),
			"unread_count": self.get_unread_count(),
			"top_recipients": self.get_top_recipients(),
			"notification_trends": self.get_notification_trends()
		}
		
		self.dashboard_data = json.dumps(data)
		self.save(ignore_permissions=True)

	def get_total_notifications(self):
		"""Get total notification count"""
		return frappe.db.count("GP Notification Log")

	def get_notifications_by_type(self):
		"""Get notifications grouped by type"""
		return frappe.db.sql("""
			SELECT 
				notification_type,
				COUNT(*) as count
			FROM `tabGP Notification Log`
			WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
			GROUP BY notification_type
			ORDER BY count DESC
		""", as_dict=True)

	def get_notifications_by_status(self):
		"""Get notifications grouped by read status"""
		return frappe.db.sql("""
			SELECT 
				CASE 
					WHEN is_read = 1 THEN 'Read'
					ELSE 'Unread'
				END as status,
				COUNT(*) as count
			FROM `tabGP Notification Log`
			WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
			GROUP BY is_read
		""", as_dict=True)

	def get_recent_notifications(self, limit=10):
		"""Get recent notifications"""
		return frappe.db.sql("""
			SELECT 
				title,
				body,
				notification_type,
				created_at,
				is_read
			FROM `tabGP Notification Log`
			ORDER BY created_at DESC
			LIMIT %s
		""", (limit,), as_dict=True)

	def get_unread_count(self):
		"""Get unread notification count"""
		return frappe.db.count("GP Notification Log", {"is_read": 0})

	def get_top_recipients(self, limit=10):
		"""Get top notification recipients"""
		return frappe.db.sql("""
			SELECT 
				recipient_user,
				COUNT(*) as count
			FROM `tabGP Notification Log`
			WHERE recipient_user IS NOT NULL
			AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
			GROUP BY recipient_user
			ORDER BY count DESC
			LIMIT %s
		""", (limit,), as_dict=True)

	def get_notification_trends(self, days=30):
		"""Get notification trends over time"""
		return frappe.db.sql("""
			SELECT 
				DATE(created_at) as date,
				COUNT(*) as count
			FROM `tabGP Notification Log`
			WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
			GROUP BY DATE(created_at)
			ORDER BY date DESC
		""", (days,), as_dict=True)

	@staticmethod
	def get_dashboard_data():
		"""Get dashboard data for API"""
		dashboard = frappe.get_doc("GP Notification Dashboard", "1")
		if not dashboard:
			dashboard = frappe.get_doc({
				"doctype": "GP Notification Dashboard",
				"title": "Notification Dashboard",
				"description": "Real-time notification statistics"
			})
			dashboard.insert(ignore_permissions=True)
		
		dashboard.refresh_dashboard_data()
		return json.loads(dashboard.dashboard_data)
