#!/usr/bin/env python3
"""
Test notification hooks to verify they're working
"""

import frappe
import json

def test_notification_hooks():
    """Test if notification hooks are working"""
    
    print("=== Testing Notification Hooks ===")
    
    # Initialize Frappe
    frappe.init(site="gameplan.test")
    frappe.connect()
    
    try:
        # Test 1: Check if hooks are loaded
        print("1. Checking if notification hooks are loaded...")
        hooks = frappe.get_hooks("doc_events")
        if "GP Artwork Task" in hooks:
            print("   ✓ GP Artwork Task hooks are loaded")
            print(f"   ✓ Hooks: {hooks['GP Artwork Task']}")
        else:
            print("   ✗ GP Artwork Task hooks not found")
            return False
        
        # Test 2: Create a test task to trigger notification
        print("2. Creating test task to trigger notification...")
        try:
            # Create a test artwork task
            task = frappe.get_doc({
                "doctype": "GP Artwork Task",
                "title": "Test Notification Task",
                "description": "This is a test task to verify notifications",
                "status": "Draft",
                "priority": "Medium",
                "assigned_to": "Administrator",
                "workflow_type": "Sales Cycle"
            })
            task.insert(ignore_permissions=True)
            print("   ✓ Test task created successfully")
            
            # Test 3: Update task status to trigger notification
            print("3. Updating task status to trigger notification...")
            task.status = "In Progress"
            task.save()
            print("   ✓ Task status updated successfully")
            
            # Test 4: Check if notification was created
            print("4. Checking if notification was created...")
            notifications = frappe.get_all(
                "GP Notification Log",
                filters={
                    "recipient_user": "Administrator",
                    "title": ["like", "%Test Notification Task%"]
                },
                limit=5
            )
            
            if notifications:
                print(f"   ✓ Found {len(notifications)} notifications")
                for notif in notifications:
                    notif_doc = frappe.get_doc("GP Notification Log", notif.name)
                    print(f"   ✓ Notification: {notif_doc.title}")
            else:
                print("   ✗ No notifications found")
            
            # Clean up
            print("5. Cleaning up test data...")
            frappe.delete_doc("GP Artwork Task", task.name)
            for notif in notifications:
                frappe.delete_doc("GP Notification Log", notif.name)
            print("   ✓ Test data cleaned up")
            
        except Exception as e:
            print(f"   ✗ Error during task test: {e}")
            return False
        
        print("\n=== Notification hooks test completed ===")
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        return False
    finally:
        frappe.destroy()

if __name__ == "__main__":
    test_notification_hooks()
