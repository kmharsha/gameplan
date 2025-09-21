#!/usr/bin/env python3
"""
Check and fix notification system issues
Run this script in your Frappe environment
"""

import frappe
import json

def check_notification_system():
    """Check notification system configuration and fix issues"""
    
    print("=== Checking Notification System ===")
    
    # Check if GP Notification Log doctype exists
    try:
        if frappe.db.exists("DocType", "GP Notification Log"):
            print("✓ GP Notification Log doctype exists")
        else:
            print("✗ GP Notification Log doctype missing")
            return False
    except Exception as e:
        print(f"✗ Error checking GP Notification Log: {e}")
        return False
    
    # Check if notification log table exists
    try:
        if frappe.db.table_exists("GP Notification Log"):
            print("✓ GP Notification Log table exists")
        else:
            print("✗ GP Notification Log table missing")
            return False
    except Exception as e:
        print(f"✗ Error checking GP Notification Log table: {e}")
        return False
    
    # Test creating a notification
    try:
        notification = frappe.get_doc({
            "doctype": "GP Notification Log",
            "title": "Test Notification",
            "body": "This is a test notification",
            "notification_type": "System",
            "recipient_user": frappe.session.user,
            "is_read": 0
        })
        notification.insert(ignore_permissions=True)
        print("✓ Successfully created test notification")
        
        # Clean up test notification
        frappe.delete_doc("GP Notification Log", notification.name)
        print("✓ Cleaned up test notification")
        
    except Exception as e:
        print(f"✗ Error creating test notification: {e}")
        return False
    
    # Check realtime publishing
    try:
        frappe.publish_realtime("test_notification", {"message": "test"}, user=frappe.session.user)
        print("✓ Realtime publishing works")
    except Exception as e:
        print(f"✗ Error with realtime publishing: {e}")
        return False
    
    print("✓ Notification system is working correctly")
    return True

def fix_notification_permissions():
    """Fix notification system permissions"""
    
    print("\n=== Fixing Notification Permissions ===")
    
    try:
        # Ensure proper permissions for GP Notification Log
        doc = frappe.get_doc("DocType", "GP Notification Log")
        
        # Add permissions if missing
        permissions = [
            {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1, "import": 1, "print": 1, "email": 1, "share": 1, "set_user_permissions": 1},
            {"role": "Gameplan Admin", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "report": 1, "export": 1, "import": 1, "print": 1, "email": 1, "share": 1, "set_user_permissions": 1},
            {"role": "Gameplan Member", "read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0, "amend": 0, "report": 0, "export": 0, "import": 0, "print": 0, "email": 0, "share": 0, "set_user_permissions": 0}
        ]
        
        for perm in permissions:
            existing_perm = None
            for p in doc.permissions:
                if p.role == perm["role"]:
                    existing_perm = p
                    break
            
            if not existing_perm:
                doc.append("permissions", perm)
                print(f"✓ Added permissions for {perm['role']}")
            else:
                print(f"✓ Permissions already exist for {perm['role']}")
        
        doc.save()
        print("✓ Updated GP Notification Log permissions")
        
    except Exception as e:
        print(f"✗ Error fixing permissions: {e}")

def check_api_endpoints():
    """Check API endpoints for issues"""
    
    print("\n=== Checking API Endpoints ===")
    
    # Check if API methods are properly whitelisted
    api_methods = [
        "gameplan.api.get_unread_count",
        "gameplan.api.send_notification",
        "gameplan.api.send_custom_notification"
    ]
    
    for method in api_methods:
        try:
            # Check if method exists in whitelist
            if frappe.db.exists("API Method", method):
                print(f"✓ {method} is whitelisted")
            else:
                print(f"✗ {method} is not whitelisted")
        except Exception as e:
            print(f"✗ Error checking {method}: {e}")

if __name__ == "__main__":
    frappe.init(site="your-site-name")  # Replace with your site name
    frappe.connect()
    
    try:
        check_notification_system()
        fix_notification_permissions()
        check_api_endpoints()
        
        print("\n=== All checks completed ===")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        frappe.destroy()
