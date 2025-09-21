# GP Device Registration DocType
# Stores device information for cross-device notifications

import frappe
from frappe.model.document import Document
from frappe.utils import now
import json

class GPDeviceRegistration(Document):
    def before_save(self):
        """Set created_at timestamp if not set"""
        if not self.created_at:
            self.created_at = now()
    
    def update_last_seen(self):
        """Update last seen timestamp and mark as online"""
        self.last_seen = now()
        self.is_online = 1
        self.save(ignore_permissions=True)
    
    def mark_offline(self):
        """Mark device as offline"""
        self.is_online = 0
        self.save(ignore_permissions=True)
    
    @staticmethod
    def register_device(user_id, device_id, device_type, user_agent, session_id=None, ip_address=None, browser_info=None):
        """Register or update device information"""
        try:
            # Check if device already exists
            existing_device = frappe.get_value(
                "GP Device Registration",
                {"device_id": device_id, "user_id": user_id},
                "name"
            )
            
            if existing_device:
                # Update existing device
                device = frappe.get_doc("GP Device Registration", existing_device)
                device.device_type = device_type
                device.user_agent = user_agent
                device.session_id = session_id
                device.ip_address = ip_address
                device.browser_info = json.dumps(browser_info) if browser_info else None
                device.update_last_seen()
                
                return {
                    "success": True,
                    "message": "Device updated successfully",
                    "device_id": device_id,
                    "action": "updated"
                }
            else:
                # Create new device registration
                device = frappe.get_doc({
                    "doctype": "GP Device Registration",
                    "device_id": device_id,
                    "user_id": user_id,
                    "device_type": device_type,
                    "user_agent": user_agent,
                    "session_id": session_id,
                    "ip_address": ip_address,
                    "browser_info": json.dumps(browser_info) if browser_info else None,
                    "is_online": 1,
                    "last_seen": now(),
                    "created_at": now()
                })
                device.insert(ignore_permissions=True)
                
                return {
                    "success": True,
                    "message": "Device registered successfully",
                    "device_id": device_id,
                    "action": "created"
                }
                
        except Exception as e:
            frappe.log_error(f"Device registration failed: {str(e)}")
            return {
                "success": False,
                "message": f"Device registration failed: {str(e)}"
            }
    
    @staticmethod
    def get_user_devices(user_id, online_only=True):
        """Get all devices for a user"""
        try:
            filters = {"user_id": user_id}
            if online_only:
                filters["is_online"] = 1
            
            devices = frappe.get_all(
                "GP Device Registration",
                filters=filters,
                fields=[
                    "device_id",
                    "device_type", 
                    "user_agent",
                    "is_online",
                    "last_seen",
                    "session_id",
                    "ip_address",
                    "browser_info"
                ],
                order_by="last_seen desc"
            )
            
            return devices
            
        except Exception as e:
            frappe.log_error(f"Failed to get user devices: {str(e)}")
            return []
    
    @staticmethod
    def cleanup_old_devices(days=30):
        """Clean up devices that haven't been seen for specified days"""
        try:
            from frappe.utils import add_days
            
            cutoff_date = add_days(now(), -days)
            
            old_devices = frappe.get_all(
                "GP Device Registration",
                filters={
                    "last_seen": ["<", cutoff_date]
                },
                fields=["name"]
            )
            
            for device in old_devices:
                frappe.delete_doc("GP Device Registration", device.name, ignore_permissions=True)
            
            return len(old_devices)
            
        except Exception as e:
            frappe.log_error(f"Device cleanup failed: {str(e)}")
            return 0
