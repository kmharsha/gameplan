#!/usr/bin/env python3

import frappe

def execute():
    """Clean up existing artwork data and reset naming series"""
    print("Cleaning up artwork data...")
    
    # Delete all existing GP Artwork records
    frappe.db.delete("GP Artwork")
    print("✓ Deleted all GP Artwork records")
    
    # Delete all existing GP Artwork Task records  
    frappe.db.delete("GP Artwork Task")
    print("✓ Deleted all GP Artwork Task records")
    
    # Delete all existing GP Artwork Status History records
    frappe.db.delete("GP Artwork Status History") 
    print("✓ Deleted all GP Artwork Status History records")
    
    # Reset the naming series for GP Artwork
    frappe.db.delete("Series", {"name": "ART-.####."})
    print("✓ Reset ART naming series")
    
    # Commit the changes
    frappe.db.commit()
    print("✓ Changes committed to database")
    
    print("Artwork data cleanup completed successfully!")
