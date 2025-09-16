#!/usr/bin/env python3
"""
Test script for the new workflow system with Sales and Procurement cycles.
This script tests the complete workflow from Sales Cycle to Procurement Cycle.
"""

import frappe
import json
from datetime import datetime

def test_workflow_system():
    """Test the complete workflow system"""
    print("🚀 Testing Workflow System...")
    
    # Test 1: Create a Sales Cycle task
    print("\n1. Creating Sales Cycle task...")
    sales_task = frappe.new_doc("GP Artwork Task")
    sales_task.title = "Test Sales Task - Logo Design"
    sales_task.artwork = "ART-001"  # Assuming this artwork exists
    sales_task.workflow_type = "Sales Cycle"
    sales_task.status = "Draft"
    sales_task.description = "Create a new logo for the client"
    sales_task.priority = "High"
    sales_task.assigned_to = "Administrator"
    sales_task.insert()
    
    print(f"✅ Sales task created: {sales_task.name}")
    print(f"   Title: {sales_task.title}")
    print(f"   Status: {sales_task.status}")
    print(f"   Workflow Type: {sales_task.workflow_type}")
    
    # Test 2: Move Sales task to Quality Review
    print("\n2. Moving Sales task to Quality Review...")
    sales_task.status = "Quality Review"
    sales_task.save()
    
    print(f"✅ Sales task moved to Quality Review")
    print(f"   Status: {sales_task.status}")
    
    # Test 3: Quality approves Sales task (moves to Completed)
    print("\n3. Quality approving Sales task...")
    sales_task.status = "Completed"
    sales_task.save()
    
    print(f"✅ Sales task completed")
    print(f"   Status: {sales_task.status}")
    print(f"   Workflow Type: {sales_task.workflow_type}")
    print(f"   Cycle Count: {sales_task.cycle_count}")
    
    # Test 4: Verify task moved to Bucket
    print("\n4. Verifying task moved to Procurement Bucket...")
    sales_task.reload()
    
    if sales_task.status == "Bucket" and sales_task.workflow_type == "Procurement Cycle":
        print("✅ Task successfully moved to Procurement Bucket")
        print(f"   Status: {sales_task.status}")
        print(f"   Workflow Type: {sales_task.workflow_type}")
        print(f"   Cycle Count: {sales_task.cycle_count}")
    else:
        print("❌ Task did not move to Bucket correctly")
        print(f"   Status: {sales_task.status}")
        print(f"   Workflow Type: {sales_task.workflow_type}")
    
    # Test 5: Create a Procurement Cycle task from Bucket
    print("\n5. Creating Procurement Cycle task from Bucket...")
    procurement_task = frappe.new_doc("GP Artwork Task")
    procurement_task.title = "Test Procurement Task - Vendor Selection"
    procurement_task.artwork = "ART-001"
    procurement_task.workflow_type = "Procurement Cycle"
    procurement_task.status = "Draft"
    procurement_task.description = "Select vendor for logo production"
    procurement_task.priority = "Medium"
    procurement_task.sales_cycle_reference = sales_task.name
    procurement_task.cycle_count = sales_task.cycle_count
    procurement_task.insert()
    
    print(f"✅ Procurement task created: {procurement_task.name}")
    print(f"   Title: {procurement_task.title}")
    print(f"   Status: {procurement_task.status}")
    print(f"   Workflow Type: {procurement_task.workflow_type}")
    print(f"   Sales Reference: {procurement_task.sales_cycle_reference}")
    
    # Test 6: Move Procurement task through workflow
    print("\n6. Moving Procurement task through workflow...")
    
    # Draft -> Procurement Review
    procurement_task.status = "Procurement Review"
    procurement_task.save()
    print(f"✅ Moved to Procurement Review")
    
    # Procurement Review -> Quality Review
    procurement_task.status = "Quality Review"
    procurement_task.save()
    print(f"✅ Moved to Quality Review")
    
    # Quality Review -> Final Approved
    procurement_task.status = "Final Approved"
    procurement_task.save()
    print(f"✅ Moved to Final Approved")
    
    # Test 7: Test role-based permissions
    print("\n7. Testing role-based permissions...")
    
    # Test Sales Role permissions
    sales_role_permissions = test_role_permissions("Sales Role", sales_task.name)
    print(f"Sales Role permissions: {sales_role_permissions}")
    
    # Test Procurement Role permissions
    procurement_role_permissions = test_role_permissions("Procurement Role", procurement_task.name)
    print(f"Procurement Role permissions: {procurement_role_permissions}")
    
    # Test Quality Role permissions
    quality_role_permissions = test_role_permissions("Quality Role", sales_task.name)
    print(f"Quality Role permissions: {quality_role_permissions}")
    
    print("\n🎉 Workflow system test completed!")
    
    return {
        "sales_task": sales_task.name,
        "procurement_task": procurement_task.name,
        "sales_role_permissions": sales_role_permissions,
        "procurement_role_permissions": procurement_role_permissions,
        "quality_role_permissions": quality_role_permissions
    }

def test_role_permissions(role, task_name):
    """Test permissions for a specific role"""
    try:
        # This is a simplified test - in reality, you'd need to test with actual user sessions
        task = frappe.get_doc("GP Artwork Task", task_name)
        
        # Check if role can access the task based on workflow type
        if role == "Sales Role":
            return task.workflow_type == "Sales Cycle"
        elif role == "Procurement Role":
            return task.workflow_type == "Procurement Cycle"
        elif role == "Quality Role":
            return True  # Quality can see both
        else:
            return False
    except Exception as e:
        print(f"Error testing permissions for {role}: {e}")
        return False

def test_api_endpoints():
    """Test the API endpoints"""
    print("\n🔌 Testing API endpoints...")
    
    try:
        # Test get_customers
        customers = frappe.call("gameplan.api.get_customers")
        print(f"✅ get_customers: {len(customers)} customers found")
        
        # Test get_artwork_kanban_data
        kanban_data = frappe.call("gameplan.api.get_artwork_kanban_data")
        print(f"✅ get_artwork_kanban_data: {len(kanban_data)} status columns")
        
        # Test get_bucket_tasks
        bucket_tasks = frappe.call("gameplan.api.get_bucket_tasks")
        print(f"✅ get_bucket_tasks: {len(bucket_tasks)} tasks in bucket")
        
        # Test get_workflow_summary
        summary = frappe.call("gameplan.api.get_workflow_summary")
        print(f"✅ get_workflow_summary: {summary}")
        
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    # Initialize Frappe
    frappe.init(site="localhost")
    frappe.connect()
    
    try:
        # Run tests
        results = test_workflow_system()
        test_api_endpoints()
        
        print("\n📊 Test Results Summary:")
        print(f"Sales Task: {results['sales_task']}")
        print(f"Procurement Task: {results['procurement_task']}")
        print(f"Sales Role Access: {results['sales_role_permissions']}")
        print(f"Procurement Role Access: {results['procurement_role_permissions']}")
        print(f"Quality Role Access: {results['quality_role_permissions']}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        frappe.destroy()