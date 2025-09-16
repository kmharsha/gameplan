#!/usr/bin/env python3

import frappe
import json

def execute():
    """Debug artwork APIs and data"""
    print("=== Debugging Artwork APIs ===")
    
    # Check if any artworks exist
    artworks = frappe.get_all("GP Artwork", fields=["name", "title", "customer", "status", "priority"])
    print(f"\n✓ Found {len(artworks)} artworks in database:")
    for artwork in artworks:
        print(f"  - {artwork.name}: {artwork.title} (Customer: {artwork.customer})")
    
    if not artworks:
        print("❌ No artworks found! This might be why the dropdown is empty.")
        return
    
    # Check customers (GP Projects)
    customers = frappe.get_all("GP Project", fields=["name", "title"])
    print(f"\n✓ Found {len(customers)} customers (GP Projects):")
    for customer in customers:
        print(f"  - {customer.name}: {customer.title}")
    
    # Test the get_customer_artworks API for each customer
    print("\n=== Testing get_customer_artworks API ===")
    for customer in customers[:3]:  # Test first 3 customers
        try:
            from gameplan.api import get_customer_artworks
            customer_artworks = get_customer_artworks(customer.name)
            print(f"✓ Customer '{customer.title}' has {len(customer_artworks)} artworks:")
            for artwork in customer_artworks:
                print(f"  - {artwork['name']}: {artwork['title']}")
        except Exception as e:
            print(f"❌ Error getting artworks for customer '{customer.title}': {str(e)}")
    
    print("\n=== Debugging Complete ===")
