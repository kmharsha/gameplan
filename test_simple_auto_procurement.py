#!/usr/bin/env python3

import frappe

def simple_test():
    """Simple test to check if the automatic procurement task creation works"""
    
    print("🧪 Simple Auto Procurement Test")
    print("=" * 40)
    
    # Initialize Frappe
    frappe.init(site="gameplan.localhost")
    frappe.connect()
    
    try:
        # Try to create a simple sales task and complete it
        print("🔨 Creating test sales task...")
        
        # First, let's check if we have any existing artworks
        artworks = frappe.get_all("GP Artwork", limit=1)
        if not artworks:
            print("❌ No artworks found. Please create an artwork first.")
            return
            
        artwork_name = artworks[0].name
        print(f"✅ Using artwork: {artwork_name}")
        
        # Create sales task
        sales_task = frappe.new_doc("GP Artwork Task")
        sales_task.title = "Test Sales Task for Auto Procurement"
        sales_task.artwork = artwork_name
        sales_task.workflow_type = "Sales Cycle"
        sales_task.status = "Draft"
        sales_task.priority = "Medium"
        
        # Get customer from artwork
        artwork_doc = frappe.get_doc("GP Artwork", artwork_name)
        sales_task.customer = artwork_doc.customer
        
        sales_task.insert(ignore_permissions=True)
        print(f"✅ Created sales task: {sales_task.name}")
        
        # Test the change_status method directly
        print("🚀 Testing status change to Completed...")
        try:
            result = sales_task.change_status("Completed", "Test completion", "Testing auto procurement creation")
            print("✅ Status change successful!")
            
            # Check if procurement task was created
            procurement_tasks = frappe.get_all("GP Artwork Task", 
                filters={
                    "sales_cycle_reference": sales_task.name,
                    "workflow_type": "Procurement Cycle"
                }
            )
            
            if procurement_tasks:
                print(f"🎉 SUCCESS! Auto-created {len(procurement_tasks)} procurement task(s)")
                for task in procurement_tasks:
                    print(f"   📦 Procurement Task: {task.name}")
            else:
                print("❌ No procurement task was created")
                
        except Exception as e:
            print(f"❌ Error during status change: {e}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        frappe.destroy()

if __name__ == "__main__":
    simple_test()
