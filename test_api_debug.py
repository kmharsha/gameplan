#!/usr/bin/env python3
"""
Debug script to test API functionality
"""
import frappe


def test_basic_api():
    """Test basic API functionality"""
    print("=== API Debug Test ===\n")
    
    frappe.set_user("Administrator")
    
    # Test 1: Check if we can import the API module
    try:
        from gameplan import api
        print("✓ Successfully imported gameplan.api")
    except Exception as e:
        print(f"❌ Failed to import gameplan.api: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Check specific API function
    try:
        print("Testing get_approved_artwork_tasks...")
        result = api.get_approved_artwork_tasks()
        print(f"✓ get_approved_artwork_tasks returned: {len(result)} tasks")
    except Exception as e:
        print(f"❌ get_approved_artwork_tasks failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Check basic Frappe DB operations
    try:
        print("Testing basic database query...")
        count = frappe.db.count("GP Artwork Task")
        print(f"✓ Database query successful. GP Artwork Task count: {count}")
    except Exception as e:
        print(f"❌ Database query failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Check DocType exists
    try:
        print("Checking if GP Artwork Task DocType exists...")
        doctype_exists = frappe.db.exists("DocType", "GP Artwork Task")
        print(f"✓ GP Artwork Task DocType exists: {doctype_exists}")
    except Exception as e:
        print(f"❌ DocType check failed: {str(e)}")
        import traceback
        traceback.print_exc()

    # Test 5: Try to get a document
    try:
        print("Testing document retrieval...")
        tasks = frappe.get_all("GP Artwork Task", limit=1)
        print(f"✓ Retrieved {len(tasks)} tasks")
        if tasks:
            print(f"  Sample task: {tasks[0]}")
    except Exception as e:
        print(f"❌ Document retrieval failed: {str(e)}")
        import traceback
        traceback.print_exc()


def execute():
    """Main execution function"""
    test_basic_api()


if __name__ == "__main__":
    execute()
