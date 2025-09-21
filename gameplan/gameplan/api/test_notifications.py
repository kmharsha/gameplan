"""
Test API for notifications
"""
import frappe
from frappe import _
from gameplan.gameplan.utils.notifications import NotificationManager

@frappe.whitelist()
def send_test_notification():
	"""Send a test notification to current user"""
	user = frappe.session.user
	
	notification = NotificationManager.send_custom_notification(
		title="Test Notification from Frontend",
		body="This notification was sent from the frontend test button!",
		recipient_user=user,
		data={"test": True, "source": "frontend"}
	)
	
	return {
		"success": True,
		"message": "Test notification sent successfully!",
		"notification_id": notification.name
	}

@frappe.whitelist()
def get_notification_count():
	"""Get notification count for current user"""
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

@frappe.whitelist()
def check_websocket_connection():
	"""Check if WebSocket is working"""
	return {
		"websocket_url": f"ws://{frappe.local.site}:{frappe.conf.webserver_port}/socket.io/",
		"site_name": frappe.local.site,
		"user": frappe.session.user
	}
