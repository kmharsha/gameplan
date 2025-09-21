#!/usr/bin/env python3

import frappe
import json

def setup_doctype():
    """Setup the GP Device Registration doctype"""
    
    # Initialize Frappe
    frappe.init(site='gameplan.test')
    frappe.connect()
    
    try:
        # Check if doctype already exists
        if frappe.db.exists("DocType", "GP Device Registration"):
            print("DocType already exists!")
            return
        
        # Create the doctype using the JSON file
        json_path = '/Users/harshakm/frappe-bench/apps/gameplan/gameplan/gameplan/doctype/gp_device_registration/gp_device_registration.json'
        
        with open(json_path, 'r') as f:
            doctype_data = json.load(f)
        
        # Create the doctype document
        doctype = frappe.new_doc("DocType")
        doctype.update(doctype_data)
        
        # Save the doctype
        doctype.insert()
        frappe.db.commit()
        
        print("DocType created successfully!")
        
        # Sync the doctype
        frappe.model.sync.sync_doctype("GP Device Registration")
        print("DocType synced successfully!")
        
    except Exception as e:
        print(f"Error setting up doctype: {str(e)}")
        frappe.log_error(f"Error setting up doctype: {str(e)}")
        raise e
    finally:
        frappe.destroy()

if __name__ == "__main__":
    setup_doctype()
