#!/usr/bin/env python3
"""
Setup script for the Workflow System.
This script initializes the workflow system and creates necessary data.
"""

import frappe
from datetime import datetime

def setup_workflow_system():
    """Setup the workflow system"""
    print("🚀 Setting up Workflow System...")
    
    # 1. Create test artwork
    print("\n1. Creating test artwork...")
    try:
        artwork = frappe.new_doc("GP Artwork")
        artwork.title = "Test Artwork - Logo Design"
        artwork.customer = "PROJ-001"  # Assuming this project exists
        artwork.description = "Test artwork for workflow system"
        artwork.priority = "High"
        artwork.project_type = "Logo Design"
        artwork.estimated_hours = 40
        artwork.budget = 5000
        artwork.insert()
        print(f"✅ Test artwork created: {artwork.name}")
    except Exception as e:
        print(f"❌ Error creating artwork: {e}")
        return False
    
    # 2. Create test customer (project)
    print("\n2. Creating test customer...")
    try:
        customer = frappe.new_doc("GP Project")
        customer.title = "Test Customer - ABC Corp"
        customer.description = "Test customer for workflow system"
        customer.icon = "🏢"
        customer.insert()
        print(f"✅ Test customer created: {customer.name}")
    except Exception as e:
        print(f"❌ Error creating customer: {e}")
        return False
    
    # 3. Create test users with roles
    print("\n3. Creating test users...")
    users_created = []
    
    # Sales User
    try:
        sales_user = frappe.new_doc("User")
        sales_user.email = "sales@test.com"
        sales_user.first_name = "Sales"
        sales_user.last_name = "User"
        sales_user.enabled = 1
        sales_user.new_password = "test123"
        sales_user.insert()
        
        # Add Sales Role
        sales_user.add_roles("Sales Role")
        users_created.append("Sales User")
        print(f"✅ Sales user created: {sales_user.email}")
    except Exception as e:
        print(f"❌ Error creating sales user: {e}")
    
    # Procurement User
    try:
        procurement_user = frappe.new_doc("User")
        procurement_user.email = "procurement@test.com"
        procurement_user.first_name = "Procurement"
        procurement_user.last_name = "User"
        procurement_user.enabled = 1
        procurement_user.new_password = "test123"
        procurement_user.insert()
        
        # Add Procurement Role
        procurement_user.add_roles("Procurement Role")
        users_created.append("Procurement User")
        print(f"✅ Procurement user created: {procurement_user.email}")
    except Exception as e:
        print(f"❌ Error creating procurement user: {e}")
    
    # Quality User
    try:
        quality_user = frappe.new_doc("User")
        quality_user.email = "quality@test.com"
        quality_user.first_name = "Quality"
        quality_user.last_name = "User"
        quality_user.enabled = 1
        quality_user.new_password = "test123"
        quality_user.insert()
        
        # Add Quality Role
        quality_user.add_roles("Quality Role")
        users_created.append("Quality User")
        print(f"✅ Quality user created: {quality_user.email}")
    except Exception as e:
        print(f"❌ Error creating quality user: {e}")
    
    # 4. Create sample tasks
    print("\n4. Creating sample tasks...")
    
    # Sales Cycle Task
    try:
        sales_task = frappe.new_doc("GP Artwork Task")
        sales_task.title = "Sample Sales Task - Logo Design"
        sales_task.artwork = artwork.name
        sales_task.workflow_type = "Sales Cycle"
        sales_task.status = "Draft"
        sales_task.description = "Create a new logo design for the client"
        sales_task.priority = "High"
        sales_task.assigned_to = "sales@test.com"
        sales_task.insert()
        print(f"✅ Sales task created: {sales_task.name}")
    except Exception as e:
        print(f"❌ Error creating sales task: {e}")
    
    # Procurement Cycle Task
    try:
        procurement_task = frappe.new_doc("GP Artwork Task")
        procurement_task.title = "Sample Procurement Task - Vendor Selection"
        procurement_task.artwork = artwork.name
        procurement_task.workflow_type = "Procurement Cycle"
        procurement_task.status = "Bucket"
        procurement_task.description = "Select vendor for logo production"
        procurement_task.priority = "Medium"
        procurement_task.assigned_to = "procurement@test.com"
        procurement_task.cycle_count = 1
        procurement_task.insert()
        print(f"✅ Procurement task created: {procurement_task.name}")
    except Exception as e:
        print(f"❌ Error creating procurement task: {e}")
    
    # 5. Test API endpoints
    print("\n5. Testing API endpoints...")
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
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
    
    print("\n🎉 Workflow system setup completed!")
    print(f"Users created: {', '.join(users_created)}")
    print("\n📋 Next steps:")
    print("1. Login with test users to test role-based access")
    print("2. Run test_workflow_system.py to test the complete workflow")
    print("3. Access the frontend to see the Kanban board and Bucket")
    
    return True

if __name__ == "__main__":
    # Initialize Frappe
    frappe.init(site="localhost")
    frappe.connect()
    
    try:
        success = setup_workflow_system()
        if success:
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup failed!")
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        frappe.destroy()
