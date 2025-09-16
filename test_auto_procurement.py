#!/usr/bin/env python3

import frappe
import json

def test_auto_procurement_creation():
    """Test the automatic procurement task creation when sales task is completed"""
    
    print("🧪 Testing Automatic Procurement Task Creation")
    print("=" * 50)
    
    # Find or create a test artwork
    try:
        artwork = frappe.get_doc("GP Artwork", {"title": "Test Artwork for Auto Procurement"})
    except:
        # Create test artwork if it doesn't exist
        try:
            # First ensure we have a test customer/project
            try:
                customer = frappe.get_doc("GP Project", {"title": "Test Customer"})
            except:
                customer = frappe.new_doc("GP Project")
                customer.title = "Test Customer"
                customer.insert(ignore_permissions=True)
                print(f"✅ Created test customer: {customer.name}")
            
            artwork = frappe.new_doc("GP Artwork")
            artwork.title = "Test Artwork for Auto Procurement"
            artwork.customer = customer.name
            artwork.description = "Test artwork for automatic procurement task creation"
            artwork.insert(ignore_permissions=True)
            print(f"✅ Created test artwork: {artwork.name}")
        except Exception as e:
            print(f"❌ Error creating test artwork: {e}")
            return
    
    # Create a Sales Cycle task
    try:
        sales_task = frappe.new_doc("GP Artwork Task")
        sales_task.title = "Test Sales Task - Auto Procurement"
        sales_task.artwork = artwork.name
        sales_task.customer = artwork.customer
        sales_task.workflow_type = "Sales Cycle"
        sales_task.status = "Draft"
        sales_task.description = "Test sales task that should auto-create procurement task when completed"
        sales_task.priority = "Medium"
        
        sales_task.insert(ignore_permissions=True)
        print(f"✅ Created sales task: {sales_task.name} ({sales_task.title})")
        
        # Check initial status
        print(f"📋 Initial status: {sales_task.status}")
        
        # Move through workflow to completed
        print("\n🔄 Moving through Sales workflow...")
        
        # Draft -> Design
        sales_task.change_status("Design", "Moving to design phase", "Starting design work")
        print(f"📋 Status changed to: {sales_task.status}")
        
        # Design -> Approval
        sales_task.change_status("Approval", "Design completed", "Ready for approval")
        print(f"📋 Status changed to: {sales_task.status}")
        
        # Approval -> Completed (This should trigger automatic procurement task creation)
        print(f"\n🚀 Completing sales task - this should auto-create procurement task...")
        sales_task.change_status("Completed", "Sales work finished", "All sales activities completed")
        print(f"📋 Sales task status: {sales_task.status}")
        
        # Check if procurement task was created
        print(f"\n🔍 Checking for auto-created procurement task...")
        procurement_tasks = frappe.get_all("GP Artwork Task", 
            filters={
                "sales_cycle_reference": sales_task.name,
                "workflow_type": "Procurement Cycle"
            },
            fields=["name", "title", "status", "workflow_type", "sales_cycle_reference"]
        )
        
        if procurement_tasks:
            print(f"✅ SUCCESS! Auto-created procurement task found:")
            for task in procurement_tasks:
                print(f"   📦 Task ID: {task.name}")
                print(f"   📦 Title: {task.title}")
                print(f"   📦 Status: {task.status}")
                print(f"   📦 Workflow: {task.workflow_type}")
                print(f"   📦 Sales Reference: {task.sales_cycle_reference}")
                
            # Test the relationship methods
            print(f"\n🔗 Testing relationship methods...")
            related_procurement = sales_task.get_related_procurement_task()
            if related_procurement:
                print(f"✅ get_related_procurement_task() works: {related_procurement}")
            else:
                print(f"❌ get_related_procurement_task() returned None")
                
            # Test from procurement side
            procurement_task = frappe.get_doc("GP Artwork Task", procurement_tasks[0].name)
            related_sales = procurement_task.get_related_sales_task()
            if related_sales:
                print(f"✅ get_related_sales_task() works: {related_sales}")
            else:
                print(f"❌ get_related_sales_task() returned None")
                
        else:
            print(f"❌ FAILED! No procurement task was auto-created")
            
        print(f"\n📊 Test Summary:")
        print(f"   Sales Task: {sales_task.name} (Status: {sales_task.status})")
        print(f"   Procurement Tasks Found: {len(procurement_tasks)}")
        
        return sales_task, procurement_tasks
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    frappe.init(site="gameplan.test")
    frappe.connect()
    
    try:
        test_auto_procurement_creation()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        frappe.destroy()
