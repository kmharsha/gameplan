# Cross-Device Notification API
# Handles sending notifications to all devices where a user is logged in

import frappe
from frappe import _
from frappe.utils import now
import json

@frappe.whitelist()
def send_to_all_devices(user_id, title, body, notification_type="System", data=None):
    """
    Send notification to all devices where the user is logged in
    """
    try:
        # Get all active sessions for the user
        active_sessions = get_user_active_sessions(user_id)
        
        if not active_sessions:
            return {
                "success": False,
                "message": "No active sessions found for user",
                "devices_notified": 0
            }
        
        # Create notification for each device
        notifications_sent = 0
        for session in active_sessions:
            try:
                # Create notification record
                notification = frappe.get_doc({
                    "doctype": "GP Notification Log",
                    "title": title,
                    "body": body,
                    "notification_type": notification_type,
                    "recipient_user": user_id,
                    "recipient_role": None,
                    "reference_doctype": None,
                    "reference_name": None,
                    "data": json.dumps(data) if data else None,
                    "is_read": 0,
                    "device_id": session.get("device_id"),
                    "session_id": session.get("session_id")
                })
                notification.insert(ignore_permissions=True)
                
                # Publish real-time notification
                frappe.publish_realtime(
                    "new_notification",
                    {
                        "title": title,
                        "body": body,
                        "notification_type": notification_type,
                        "data": data,
                        "device_id": session.get("device_id"),
                        "session_id": session.get("session_id")
                    },
                    user=user_id
                )
                
                notifications_sent += 1
                
            except Exception as e:
                frappe.log_error(f"Failed to send notification to device {session.get('device_id')}: {str(e)}")
                continue
        
        return {
            "success": True,
            "message": f"Notifications sent to {notifications_sent} devices",
            "devices_notified": notifications_sent,
            "total_devices": len(active_sessions)
        }
        
    except Exception as e:
        frappe.log_error(f"Cross-device notification failed: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to send notifications: {str(e)}",
            "devices_notified": 0
        }

@frappe.whitelist()
def register_device(user_id, device_id, device_type, user_agent, session_id=None, ip_address=None, browser_info=None):
    """
    Register a device for cross-device notifications
    """
    try:
        from gameplan.gameplan.doctype.gp_device_registration.gp_device_registration import GPDeviceRegistration
        
        # Register device using the doctype
        result = GPDeviceRegistration.register_device(
            user_id=user_id,
            device_id=device_id,
            device_type=device_type,
            user_agent=user_agent,
            session_id=session_id,
            ip_address=ip_address,
            browser_info=browser_info
        )
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Device registration failed: {str(e)}")
        return {
            "success": False,
            "message": f"Device registration failed: {str(e)}"
        }

@frappe.whitelist()
def get_user_active_sessions(user_id):
    """
    Get all active sessions for a user from GP Device Registration doctype
    """
    try:
        from gameplan.gameplan.doctype.gp_device_registration.gp_device_registration import GPDeviceRegistration
        
        # Get all online devices for the user
        devices = GPDeviceRegistration.get_user_devices(user_id, online_only=True)
        
        # Convert to session format
        sessions = []
        for device in devices:
            sessions.append({
                "device_id": device.get("device_id"),
                "session_id": device.get("session_id"),
                "device_type": device.get("device_type"),
                "last_seen": device.get("last_seen"),
                "user_agent": device.get("user_agent"),
                "ip_address": device.get("ip_address")
            })
        
        return sessions
            
    except Exception as e:
        frappe.log_error(f"Failed to get active sessions: {str(e)}")
        return []

@frappe.whitelist()
def test_cross_device_notification(user_id=None):
    """
    Test cross-device notification
    """
    if not user_id:
        user_id = frappe.session.user
    
    return send_to_all_devices(
        user_id=user_id,
        title="Test Cross-Device Notification",
        body="This is a test notification sent to all your devices!",
        notification_type="System",
        data={"test": True, "timestamp": now()}
    )

@frappe.whitelist()
def get_user_devices(user_id=None):
    """
    Get all devices for a user
    """
    if not user_id:
        user_id = frappe.session.user
    
    try:
        from gameplan.gameplan.doctype.gp_device_registration.gp_device_registration import GPDeviceRegistration
        
        devices = GPDeviceRegistration.get_user_devices(user_id, online_only=False)
        
        return {
            "success": True,
            "devices": devices,
            "total_devices": len(devices),
            "online_devices": len([d for d in devices if d.get("is_online")])
        }
        
    except Exception as e:
        frappe.log_error(f"Failed to get user devices: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to get devices: {str(e)}",
            "devices": []
        }

@frappe.whitelist()
def cleanup_old_devices(days=30):
    """
    Clean up old device registrations
    """
    try:
        from gameplan.gameplan.doctype.gp_device_registration.gp_device_registration import GPDeviceRegistration
        
        cleaned_count = GPDeviceRegistration.cleanup_old_devices(days)
        
        return {
            "success": True,
            "message": f"Cleaned up {cleaned_count} old devices",
            "cleaned_count": cleaned_count
        }
        
    except Exception as e:
        frappe.log_error(f"Device cleanup failed: {str(e)}")
        return {
            "success": False,
            "message": f"Cleanup failed: {str(e)}",
            "cleaned_count": 0
        }
