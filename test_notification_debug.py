#!/usr/bin/env python3
"""
Test script to debug notification system
"""
import frappe
import sys
import os

# Add the frappe-bench directory to the path
sys.path.insert(0, '/Users/harshakm/frappe-bench')

# Initialize frappe
frappe.init(site='gameplan.test')
frappe.connect()

def test_notification_system():
    print("=== Testing Notification System ===")
    
    # 1. Check if GP Notification Log doctype exists
    print("\n1. Checking GP Notification Log doctype...")
    try:
        notifications = frappe.get_all("GP Notification Log", limit=5)
        print(f"   Found {len(notifications)} notifications in database")
        for notif in notifications:
            print(f"   - {notif.name}: {notif.title}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 2. Test creating a notification directly
    print("\n2. Testing direct notification creation...")
    try:
        from gameplan.gameplan.utils.notifications import NotificationManager
        
        notification = NotificationManager.send_notification(
            title="Test Notification from Script",
            body="This is a test notification created directly",
            notification_type="System",
            recipient_user="Administrator"
        )
        print(f"   Created notification: {notification.name}")
    except Exception as e:
        print(f"   Error creating notification: {e}")
    
    # 3. Check notifications again
    print("\n3. Checking notifications after creation...")
    try:
        notifications = frappe.get_all("GP Notification Log", limit=10)
        print(f"   Found {len(notifications)} notifications in database")
        for notif in notifications:
            print(f"   - {notif.name}: {notif.title}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 4. Test the API method
    print("\n4. Testing API method...")
    try:
        from gameplan.gameplan.api.notifications import get_user_notifications
        result = get_user_notifications(user="Administrator", limit=10)
        print(f"   API returned {len(result)} notifications")
        for notif in result:
            print(f"   - {notif.get('id')}: {notif.get('title')}")
    except Exception as e:
        print(f"   Error calling API: {e}")

if __name__ == "__main__":
    test_notification_system()
