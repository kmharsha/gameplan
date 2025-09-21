#!/usr/bin/env python3

import frappe
import json

def create_doctype():
    """Create the GP Device Registration doctype"""
    
    # Initialize Frappe
    frappe.init(site='gameplan.test')
    frappe.connect()
    
    try:
        # Check if doctype already exists
        if frappe.db.exists("DocType", "GP Device Registration"):
            print("DocType already exists!")
            return
        
        # Create the doctype
        doctype = frappe.new_doc("DocType")
        doctype.name = "GP Device Registration"
        doctype.module = "Gameplan"
        doctype.istable = 0
        doctype.istree = 0
        doctype.autoname = "field:device_id"
        doctype.allow_rename = 1
        doctype.track_changes = 1
        doctype.editable_grid = 1
        doctype.engine = "InnoDB"
        doctype.default_view = "List"
        doctype.sort_field = "modified"
        doctype.sort_order = "DESC"
        
        # Add fields
        fields = [
            {
                "fieldname": "device_id",
                "fieldtype": "Data",
                "label": "Device ID",
                "reqd": 1,
                "unique": 1,
                "length": 100,
                "in_list_view": 1
            },
            {
                "fieldname": "user_id",
                "fieldtype": "Link",
                "label": "User",
                "options": "User",
                "reqd": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "device_type",
                "fieldtype": "Select",
                "label": "Device Type",
                "options": "Desktop\nMobile\nPWA\nTablet",
                "reqd": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "user_agent",
                "fieldtype": "Text",
                "label": "User Agent",
                "read_only": 1
            },
            {
                "fieldname": "is_online",
                "fieldtype": "Check",
                "label": "Is Online",
                "default": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "last_seen",
                "fieldtype": "Datetime",
                "label": "Last Seen",
                "reqd": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "session_id",
                "fieldtype": "Data",
                "label": "Session ID",
                "length": 100
            },
            {
                "fieldname": "ip_address",
                "fieldtype": "Data",
                "label": "IP Address",
                "length": 45
            },
            {
                "fieldname": "browser_info",
                "fieldtype": "JSON",
                "label": "Browser Info"
            }
        ]
        
        # Add fields to doctype
        for field_data in fields:
            field = doctype.append("fields")
            field.update(field_data)
        
        # Add permissions
        permissions = [
            {
                "role": "System Manager",
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "export": 1,
                "print": 1,
                "email": 1,
                "report": 1,
                "share": 1
            },
            {
                "role": "Administrator", 
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "export": 1,
                "print": 1,
                "email": 1,
                "report": 1,
                "share": 1
            }
        ]
        
        for perm_data in permissions:
            perm = doctype.append("permissions")
            perm.update(perm_data)
        
        # Save the doctype
        doctype.insert()
        frappe.db.commit()
        
        print("DocType created successfully!")
        
        # Sync the doctype
        frappe.model.sync.sync_doctype("GP Device Registration")
        print("DocType synced successfully!")
        
    except Exception as e:
        print(f"Error creating doctype: {str(e)}")
        frappe.log_error(f"Error creating doctype: {str(e)}")
        raise e
    finally:
        frappe.destroy()

if __name__ == "__main__":
    create_doctype()
