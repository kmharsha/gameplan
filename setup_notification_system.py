#!/usr/bin/env python3
"""
Setup script for the Gameplan Notification System
This script installs and configures the notification system components
"""

import frappe
import json
import os
import sys

def setup_notification_system():
    """Setup the notification system"""
    print("Setting up Gameplan Notification System...")
    
    # Create DocTypes
    create_doctypes()
    
    # Create roles
    create_roles()
    
    # Create permissions
    create_permissions()
    
    # Create sample data
    create_sample_data()
    
    print("Notification system setup completed successfully!")
    print("\nNext steps:")
    print("1. Restart your Frappe server")
    print("2. Visit /g/notification-demo to test the system")
    print("3. Check GP Notification Sender for admin interface")
    print("4. Check GP Notification Dashboard for statistics")

def create_doctypes():
    """Create notification DocTypes"""
    print("Creating DocTypes...")
    
    # The DocTypes are already created as JSON files
    # This function can be used to create them programmatically if needed
    pass

def create_roles():
    """Create notification-related roles"""
    print("Creating roles...")
    
    roles = [
        {
            "role_name": "Sales User",
            "desk_access": 1,
            "is_custom": 1,
            "module": "Gameplan"
        },
        {
            "role_name": "Procurement User", 
            "desk_access": 1,
            "is_custom": 1,
            "module": "Gameplan"
        }
    ]
    
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.get_doc(role_data)
            role.insert(ignore_permissions=True)
            print(f"Created role: {role_data['role_name']}")

def create_permissions():
    """Create permissions for notification DocTypes"""
    print("Setting up permissions...")
    
    # Permissions are already defined in the DocType JSON files
    pass

def create_sample_data():
    """Create sample notification data"""
    print("Creating sample data...")
    
    # Create a sample notification dashboard
    if not frappe.db.exists("GP Notification Dashboard", "1"):
        dashboard = frappe.get_doc({
            "doctype": "GP Notification Dashboard",
            "title": "Notification Dashboard",
            "description": "Real-time notification statistics and analytics"
        })
        dashboard.insert(ignore_permissions=True)
        print("Created notification dashboard")

def test_notification_system():
    """Test the notification system"""
    print("Testing notification system...")
    
    try:
        # Test sending a notification
        from gameplan.utils.notifications import NotificationManager
        
        notification = NotificationManager.send_custom_notification(
            title="System Setup Complete",
            body="The Gameplan notification system has been successfully set up!",
            recipient_user=frappe.session.user
        )
        
        print("Test notification sent successfully!")
        return True
        
    except Exception as e:
        print(f"Error testing notification system: {str(e)}")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode
        if test_notification_system():
            print("Notification system test passed!")
        else:
            print("Notification system test failed!")
            sys.exit(1)
    else:
        # Setup mode
        setup_notification_system()

if __name__ == "__main__":
    main()
