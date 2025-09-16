#!/usr/bin/env python3

import frappe
from frappe import _

def execute():
    """Test all artwork functionality to identify remaining issues"""
    
    print("\n=== ARTWORK FUNCTIONALITY TEST ===\n")
    
    # Test 1: Check if we have any existing artworks
    print("1. Checking existing artworks...")
    try:
        artworks = frappe.get_all("GP Artwork", fields=["name", "title", "customer", "status"])
        print(f"   Found {len(artworks)} artworks:")
        for artwork in artworks:
            print(f"     - {artwork.name}: {artwork.title} (Customer: {artwork.customer}, Status: {artwork.status})")
    except Exception as e:
        print(f"   ERROR getting artworks: {e}")
    
    # Test 2: Check if we have any spaces (customers)
    print("\n2. Checking available spaces (customers)...")
    try:
        spaces = frappe.get_all("GP Project", fields=["name", "title"])
        print(f"   Found {len(spaces)} spaces:")
        for space in spaces[:5]:  # Show first 5
            print(f"     - {space.name}: {space.title}")
    except Exception as e:
        print(f"   ERROR getting spaces: {e}")
    
    # Test 3: Test get_customer_artworks API
    if spaces:
        print("\n3. Testing get_customer_artworks API...")
        try:
            from gameplan.api import get_customer_artworks
            customer = spaces[0]['name']
            result = get_customer_artworks(customer)
            print(f"   API called with customer='{customer}'")
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   ERROR calling get_customer_artworks: {e}")
    
    # Test 4: Test create_artwork API (if we have a space)
    if spaces:
        print("\n4. Testing create_artwork API...")
        try:
            from gameplan.api import create_artwork
            customer = spaces[0]['name']
            
            # Create a test artwork
            result = create_artwork(
                customer=customer,
                title="Test Artwork for Debug",
                description="This is a test artwork created during debugging",
                priority="Medium",
                estimated_hours=5
            )
            print(f"   Successfully created artwork: {result}")
            test_artwork_name = result['name']
            
            # Test 5: Test get_customer_artworks again to see the new artwork
            print("\n5. Re-testing get_customer_artworks after creating artwork...")
            result = get_customer_artworks(customer)
            print(f"   Updated result: {result}")
            
            # Test 6: Test update_artwork API
            print("\n6. Testing update_artwork API...")
            from gameplan.api import update_artwork
            updated = update_artwork(
                artwork_id=test_artwork_name,
                title="Updated Test Artwork",
                description="Updated description",
                priority="High"
            )
            print(f"   Successfully updated artwork: {updated}")
            
        except Exception as e:
            print(f"   ERROR in artwork creation/update test: {e}")
    
    # Test 7: Check artwork tasks
    print("\n7. Checking artwork tasks...")
    try:
        tasks = frappe.get_all("GP Artwork Task", 
                              fields=["name", "title", "artwork", "status"],
                              limit=10)
        print(f"   Found {len(tasks)} artwork tasks:")
        for task in tasks:
            print(f"     - {task.name}: {task.title} (Artwork: {task.artwork}, Status: {task.status})")
    except Exception as e:
        print(f"   ERROR getting artwork tasks: {e}")
    
    # Test 8: Test create_artwork_task API (if we have artworks)
    if artworks or 'test_artwork_name' in locals():
        print("\n8. Testing create_artwork_task API...")
        try:
            from gameplan.api import create_artwork_task
            
            # Use test artwork if created, otherwise use first existing artwork
            artwork_name = test_artwork_name if 'test_artwork_name' in locals() else artworks[0]['name']
            
            task_result = create_artwork_task(
                title="Test Artwork Task",
                artwork=artwork_name,
                description="Test task description",
                priority="Medium"
            )
            print(f"   Successfully created artwork task: {task_result}")
            
        except Exception as e:
            print(f"   ERROR creating artwork task: {e}")
    
    print("\n=== TEST COMPLETED ===\n")
    
    # Summary
    print("SUMMARY:")
    print("- Check the above output for any ERROR messages")
    print("- If artworks and spaces exist, the APIs should work")
    print("- If get_customer_artworks returns results, the dropdown should populate")
    print("- If create/update operations work, the UI should function properly")

if __name__ == "__main__":
    execute()
