#!/usr/bin/env python3
"""
Manual notification test
"""
import frappe

def test_manual_notification():
    frappe.init(site='gameplan.test')
    frappe.connect()
    
    print("Testing manual notification creation...")
    
    # Create a notification directly
    notification = frappe.get_doc({
        "doctype": "GP Notification Log",
        "title": "Manual Test Notification",
        "body": "This is a manually created test notification",
        "notification_type": "System",
        "recipient_user": "Administrator"
    })
    
    notification.insert(ignore_permissions=True)
    print(f"Created notification: {notification.name}")
    
    # Check if it exists
    notifications = frappe.get_all("GP Notification Log", 
                                 filters={"recipient_user": "Administrator"},
                                 limit=5)
    print(f"Found {len(notifications)} notifications for Administrator")
    
    for notif in notifications:
        print(f"  - {notif.name}: {notif.title}")

if __name__ == "__main__":
    test_manual_notification()
