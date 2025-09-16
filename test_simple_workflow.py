#!/usr/bin/env python3
"""
Simple test script to verify the workflow system is working
"""

import frappe
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple_workflow():
    """Test the basic workflow functionality"""
    print("Testing Simple Workflow...")
    
    try:
        # Initialize Frappe
        frappe.init(site='localhost')
        frappe.connect()
        
        print("✓ Connected to Frappe")
        
        # Test 1: Check if roles exist
        print("\n1. Checking roles...")
        roles = ["Sales Role", "Procurement Role", "Quality Role"]
        for role in roles:
            if frappe.db.exists("Role", role):
                print(f"✓ Role '{role}' exists")
            else:
                print(f"✗ Role '{role}' does not exist")
        
        # Test 2: Check DocType structure
        print("\n2. Checking DocType structure...")
        doctype = frappe.get_meta("GP Artwork Task")
        
        # Check status options
        status_field = doctype.get_field("status")
        if status_field:
            status_options = status_field.options.split('\n')
            expected_statuses = ["Draft", "Quality Review", "Rework", "Completed", "Procurement Review", "Final Approved", "Bucket"]
            for status in expected_statuses:
                if status in status_options:
                    print(f"✓ Status '{status}' available")
                else:
                    print(f"✗ Status '{status}' missing")
        
        # Check workflow_type field
        workflow_field = doctype.get_field("workflow_type")
        if workflow_field:
            workflow_options = workflow_field.options.split('\n')
            expected_workflows = ["Sales Cycle", "Procurement Cycle"]
            for workflow in expected_workflows:
                if workflow in workflow_options:
                    print(f"✓ Workflow '{workflow}' available")
                else:
                    print(f"✗ Workflow '{workflow}' missing")
        
        # Test 3: Test API endpoints
        print("\n3. Testing API endpoints...")
        
        # Test get_workflow_status_options
        try:
            sales_statuses = frappe.call("gameplan.api.get_workflow_status_options", "Sales Cycle")
            print(f"✓ Sales Cycle statuses: {sales_statuses}")
            
            procurement_statuses = frappe.call("gameplan.api.get_workflow_status_options", "Procurement Cycle")
            print(f"✓ Procurement Cycle statuses: {procurement_statuses}")
        except Exception as e:
            print(f"✗ API test failed: {e}")
        
        # Test 4: Check if we can create a task
        print("\n4. Testing task creation...")
        
        # Create a test customer
        customer = frappe.new_doc("GP Project")
        customer.title = "Test Customer for Workflow"
        customer.description = "Test customer"
        customer.insert()
        print(f"✓ Created test customer: {customer.name}")
        
        # Create a test artwork
        artwork = frappe.new_doc("GP Artwork")
        artwork.customer = customer.name
        artwork.title = "Test Artwork for Workflow"
        artwork.description = "Test artwork"
        artwork.priority = "Medium"
        artwork.insert()
        print(f"✓ Created test artwork: {artwork.name}")
        
        # Create a Sales Cycle task
        task = frappe.new_doc("GP Artwork Task")
        task.title = "Test Workflow Task"
        task.artwork = artwork.name
        task.customer = customer.name
        task.description = "Test task for workflow"
        task.priority = "Medium"
        task.workflow_type = "Sales Cycle"
        task.status = "Draft"
        task.insert()
        print(f"✓ Created Sales Cycle task: {task.name}")
        print(f"  - Workflow Type: {task.workflow_type}")
        print(f"  - Status: {task.status}")
        
        # Test 5: Test status transition
        print("\n5. Testing status transition...")
        
        # Change to Quality Review
        task.status = "Quality Review"
        task.save()
        print(f"✓ Changed status to: {task.status}")
        
        # Change to Completed (this should trigger bucket movement)
        task.status = "Completed"
        task.save()
        print(f"✓ Changed status to: {task.status}")
        
        # Check if task moved to bucket
        task.reload()
        print(f"  - Final Workflow Type: {task.workflow_type}")
        print(f"  - Final Status: {task.status}")
        print(f"  - Cycle Count: {task.cycle_count}")
        
        if task.workflow_type == "Procurement Cycle" and task.status == "Bucket":
            print("✓ Task successfully moved to Procurement Bucket!")
        else:
            print("✗ Task did not move to Bucket as expected")
        
        # Cleanup
        print("\n6. Cleaning up...")
        task.delete()
        artwork.delete()
        customer.delete()
        print("✓ Cleanup completed")
        
        print("\n✓ Simple workflow test completed!")
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        frappe.destroy()

if __name__ == "__main__":
    test_simple_workflow()


