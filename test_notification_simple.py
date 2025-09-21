#!/usr/bin/env python3
"""
Simple notification test
"""
import frappe

def test_notification():
    frappe.init(site='gameplan.test')
    frappe.connect()
    
    print("=== Testing Notification System ===")
    
    # 1. Check if GP Notification Log exists
    print("\n1. Checking GP Notification Log doctype...")
    try:
        count = frappe.db.count("GP Notification Log")
        print(f"   Total notifications in database: {count}")
        
        if count > 0:
            notifications = frappe.get_all("GP Notification Log", limit=5)
            for notif in notifications:
                print(f"   - {notif.name}: {notif.title}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 2. Test creating a notification directly
    print("\n2. Creating test notification...")
    try:
        notification = frappe.get_doc({
            "doctype": "GP Notification Log",
            "title": "Test Notification",
            "body": "This is a test notification",
            "notification_type": "System",
            "recipient_user": "Administrator"
        })
        
        notification.insert(ignore_permissions=True)
        print(f"   ✅ Created notification: {notification.name}")
        
    except Exception as e:
        print(f"   ❌ Error creating notification: {e}")
    
    # 3. Check notifications again
    print("\n3. Checking notifications after creation...")
    try:
        count = frappe.db.count("GP Notification Log")
        print(f"   Total notifications now: {count}")
        
        notifications = frappe.get_all("GP Notification Log", 
                                     filters={"recipient_user": "Administrator"},
                                     limit=5)
        print(f"   Notifications for Administrator: {len(notifications)}")
        
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
    test_notification()
