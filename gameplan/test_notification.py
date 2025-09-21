#!/usr/bin/env python3
"""
Test script to send a notification and check if the system is working
"""
import frappe
import json

def test_notification():
    """Test sending a notification"""
    try:
        # Test sending a notification using our new system
        from gameplan.gameplan.utils.notifications import NotificationManager
        
        # Send a test notification
        notification = NotificationManager.send_custom_notification(
            title="Test Notification",
            body="This is a test notification from the new system!",
            recipient_user=frappe.session.user
        )
        
        print(f"✅ Test notification sent successfully! ID: {notification.name}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending test notification: {str(e)}")
        return False

def check_notification_log():
    """Check if notifications are being created in GP Notification Log"""
    try:
        # Count notifications in our new system
        count = frappe.db.count("GP Notification Log")
        print(f"📊 Notifications in GP Notification Log: {count}")
        
        # Get recent notifications
        notifications = frappe.get_all(
            "GP Notification Log",
            fields=["name", "title", "body", "created_at"],
            order_by="created_at desc",
            limit=5
        )
        
        if notifications:
            print("📋 Recent notifications:")
            for notif in notifications:
                print(f"  - {notif.name}: {notif.title}")
        else:
            print("📋 No notifications found in GP Notification Log")
            
        return count > 0
        
    except Exception as e:
        print(f"❌ Error checking notification log: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Notification System...")
    print("=" * 50)
    
    # Check current notifications
    has_notifications = check_notification_log()
    
    # Send test notification
    test_sent = test_notification()
    
    # Check again
    print("\n" + "=" * 50)
    print("🔄 Checking after test...")
    check_notification_log()
    
    if test_sent:
        print("\n✅ Notification system is working!")
        print("💡 Check your web browser for the notification")
    else:
        print("\n❌ Notification system needs fixing")
