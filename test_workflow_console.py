#!/usr/bin/env python3
"""
Simple test script for the workflow system that can be run in Frappe console.
"""

def test_workflow_system():
    """Test the workflow system"""
    print("🚀 Testing Workflow System...")
    
    try:
        # Test 1: Check if artwork task doctype exists
        print("\n1. Checking GP Artwork Task doctype...")
        if frappe.db.exists("DocType", "GP Artwork Task"):
            print("✅ GP Artwork Task doctype exists")
        else:
            print("❌ GP Artwork Task doctype not found")
            return False
        
        # Test 2: Check if roles exist
        print("\n2. Checking roles...")
        roles = ["Sales Role", "Procurement Role", "Quality Role"]
        for role in roles:
            if frappe.db.exists("Role", role):
                print(f"✅ {role} exists")
            else:
                print(f"❌ {role} not found")
        
        # Test 3: Test API endpoints
        print("\n3. Testing API endpoints...")
        try:
            # Test get_customers
            customers = frappe.call("gameplan.api.get_customers")
            print(f"✅ get_customers: {len(customers)} customers found")
        except Exception as e:
            print(f"❌ get_customers failed: {e}")
        
        try:
            # Test get_artwork_kanban_data
            kanban_data = frappe.call("gameplan.api.get_artwork_kanban_data")
            print(f"✅ get_artwork_kanban_data: {len(kanban_data)} status columns")
        except Exception as e:
            print(f"❌ get_artwork_kanban_data failed: {e}")
        
        try:
            # Test get_bucket_tasks
            bucket_tasks = frappe.call("gameplan.api.get_bucket_tasks")
            print(f"✅ get_bucket_tasks: {len(bucket_tasks)} tasks in bucket")
        except Exception as e:
            print(f"❌ get_bucket_tasks failed: {e}")
        
        # Test 4: Check if we can create a task
        print("\n4. Testing task creation...")
        try:
            # Check if we have any artworks
            artworks = frappe.get_all("GP Artwork", limit=1)
            if artworks:
                artwork_name = artworks[0].name
                print(f"✅ Found artwork: {artwork_name}")
                
                # Try to create a test task
                task = frappe.new_doc("GP Artwork Task")
                task.title = "Test Workflow Task"
                task.artwork = artwork_name
                task.workflow_type = "Sales Cycle"
                task.status = "Draft"
                task.description = "Test task for workflow system"
                task.priority = "Medium"
                task.insert()
                print(f"✅ Test task created: {task.name}")
                
                # Test status transition
                task.status = "Quality Review"
                task.save()
                print("✅ Status transition successful")
                
                # Clean up
                task.delete()
                print("✅ Test task cleaned up")
                
            else:
                print("⚠️ No artworks found, skipping task creation test")
        except Exception as e:
            print(f"❌ Task creation test failed: {e}")
        
        print("\n🎉 Workflow system test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run the test
if __name__ == "__main__":
    test_workflow_system()
