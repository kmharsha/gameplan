#!/usr/bin/env python3
"""
Test script to verify notification system fixes
"""

import frappe
import json

def test_notification_system():
    """Test the notification system"""
    
    print("=== Testing Notification System ===")
    
    # Initialize Frappe
    frappe.init(site="gameplan.test")
    frappe.connect()
    
    try:
        # Test 1: Check if GP Notification Log doctype exists
        print("1. Checking GP Notification Log doctype...")
        if frappe.db.exists("DocType", "GP Notification Log"):
            print("   ✓ GP Notification Log doctype exists")
        else:
            print("   ✗ GP Notification Log doctype missing")
            return False
        
        # Test 2: Test creating a notification
        print("2. Testing notification creation...")
        try:
            notification = frappe.get_doc({
                "doctype": "GP Notification Log",
                "title": "Test Notification",
                "body": "This is a test notification",
                "notification_type": "System",
                "recipient_user": "Administrator",
                "is_read": 0
            })
            notification.insert(ignore_permissions=True)
            print("   ✓ Successfully created test notification")
            
            # Clean up
            frappe.delete_doc("GP Notification Log", notification.name)
            print("   ✓ Cleaned up test notification")
            
        except Exception as e:
            print(f"   ✗ Error creating notification: {e}")
            return False
        
        # Test 3: Test API method
        print("3. Testing API method...")
        try:
            from gameplan.gameplan.api.notifications import get_user_notifications
            notifications = get_user_notifications(user="Administrator", limit=5)
            print(f"   ✓ API method works, returned {len(notifications)} notifications")
        except Exception as e:
            print(f"   ✗ Error testing API method: {e}")
            return False
        
        # Test 4: Test sending notification via API
        print("4. Testing send notification API...")
        try:
            from gameplan.gameplan.api.notifications import send_system_notification
            result = send_system_notification(
                title="API Test Notification",
                body="This is a test notification from API",
                recipient_user="Administrator"
            )
            print("   ✓ Successfully sent notification via API")
            
            # Clean up
            if result and hasattr(result, 'name'):
                frappe.delete_doc("GP Notification Log", result.name)
                print("   ✓ Cleaned up API test notification")
            
        except Exception as e:
            print(f"   ✗ Error testing send notification API: {e}")
            return False
        
        print("\n=== All tests passed! ===")
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        return False
    finally:
        frappe.destroy()

if __name__ == "__main__":
    test_notification_system()
