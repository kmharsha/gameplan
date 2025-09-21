#!/usr/bin/env python3

import frappe
import json
import os

def import_doctype():
    """Import the GP Device Registration doctype"""
    
    # Initialize Frappe
    frappe.init(site='gameplan.test')
    frappe.connect()
    
    # Path to the doctype JSON file
    json_path = '/Users/harshakm/frappe-bench/apps/gameplan/gameplan/gameplan/doctype/gp_device_registration/gp_device_registration.json'
    
    try:
        # Read the JSON file
        with open(json_path, 'r') as f:
            doctype_data = json.load(f)
        
        print(f"Importing doctype: {doctype_data['name']}")
        
        # Check if doctype already exists
        if frappe.db.exists("DocType", doctype_data['name']):
            print(f"DocType {doctype_data['name']} already exists. Updating...")
            # Update existing doctype
            existing_doc = frappe.get_doc("DocType", doctype_data['name'])
            existing_doc.update(doctype_data)
            existing_doc.save()
            frappe.db.commit()
            print(f"DocType {doctype_data['name']} updated successfully!")
        else:
            print(f"Creating new doctype: {doctype_data['name']}")
            # Create new doctype
            doctype_doc = frappe.get_doc(doctype_data)
            doctype_doc.insert()
            frappe.db.commit()
            print(f"DocType {doctype_data['name']} created successfully!")
        
        # Sync the doctype
        print("Syncing doctype...")
        frappe.model.sync.sync_doctype(doctype_data['name'])
        print("DocType synced successfully!")
        
    except Exception as e:
        print(f"Error importing doctype: {str(e)}")
        frappe.log_error(f"Error importing doctype: {str(e)}")
        raise e
    finally:
        frappe.destroy()

if __name__ == "__main__":
    import_doctype()
