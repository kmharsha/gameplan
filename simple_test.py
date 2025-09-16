#!/usr/bin/env python3

import frappe

def execute():
    print("=== Checking Artwork System ===")
    
    # Check spaces/projects
    spaces = frappe.get_all("GP Project", fields=["name", "title"])
    print(f"Found {len(spaces)} spaces/projects:")
    for space in spaces:
        print(f"  - {space.name}: {space.title}")
    
    if not spaces:
        print("No spaces found - this is the problem!")
        return
    
    # Check artworks for the first space
    first_space = spaces[0]["name"]
    print(f"\nChecking artworks for space: {first_space}")
    
    artworks = frappe.get_all("GP Artwork", 
                             filters={"customer": first_space},
                             fields=["name", "title", "status"])
    print(f"Found {len(artworks)} artworks:")
    for artwork in artworks:
        print(f"  - {artwork.name}: {artwork.title} ({artwork.status})")
    
    # If no artworks, create a test one
    if not artworks:
        print(f"\nCreating test artwork for {first_space}")
        try:
            artwork = frappe.new_doc("GP Artwork")
            artwork.update({
                "customer": first_space,
                "title": "Test Artwork",
                "description": "Test artwork for debugging",
                "priority": "Medium",
                "status": "Draft",
                "estimated_hours": 10
            })
            artwork.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Created test artwork: {artwork.name}")
        except Exception as e:
            print(f"Error creating artwork: {e}")
    
    # Test the API call
    print(f"\nTesting get_customer_artworks API for {first_space}:")
    try:
        from gameplan.api import get_customer_artworks
        result = get_customer_artworks(first_space)
        print(f"API Result: {result}")
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    execute()
