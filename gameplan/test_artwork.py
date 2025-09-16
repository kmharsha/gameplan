#!/usr/bin/env python3

import frappe

def test_artwork_system():
    """Test the artwork system backend functionality"""
    
    print("=== Testing Artwork Management System Backend ===\n")
    
    # Test 1: Check if doctypes exist
    print("1. Checking DocTypes...")
    doctypes = ["GP Artwork Task", "GP Artwork Attachment", "GP Artwork Status History"]
    
    for doctype in doctypes:
        if frappe.db.exists("DocType", doctype):
            print(f"✓ {doctype} exists")
        else:
            print(f"✗ {doctype} missing")
    
    # Test 2: Check if roles exist
    print("\n2. Checking Roles...")
    roles = ["Artwork Sales Team", "Artwork Quality Team", "Artwork Procurement Team"]
    
    for role in roles:
        if frappe.db.exists("Role", role):
            print(f"✓ {role} exists")
        else:
            print(f"✗ {role} missing")
    
    # Test 3: Create a test project if needed
    print("\n3. Setting up test data...")
    
    # Create team if not exists
    if not frappe.db.exists("GP Team", {"title": "Artwork Test Team"}):
        team = frappe.get_doc({
            "doctype": "GP Team",
            "title": "Artwork Test Team",
            "description": "Test team for artwork system"
        })
        team.insert(ignore_permissions=True)
        print("✓ Created test team")
    else:
        team = frappe.get_doc("GP Team", {"title": "Artwork Test Team"})
        print("✓ Test team already exists")
    
    # Create project if not exists
    if not frappe.db.exists("GP Project", {"title": "Artwork Test Project"}):
        project = frappe.get_doc({
            "doctype": "GP Project",
            "title": "Artwork Test Project",
            "team": team.name,
            "description": "Test project for artwork tasks"
        })
        project.insert(ignore_permissions=True)
        print("✓ Created test project")
    else:
        project = frappe.get_doc("GP Project", {"title": "Artwork Test Project"})
        print("✓ Test project already exists")
    
    # Test 4: Create test artwork task
    print("\n4. Testing Artwork Task Creation...")
    
    task_title = "Backend Test Artwork Task"
    if not frappe.db.exists("GP Artwork Task", {"title": task_title}):
        task = frappe.get_doc({
            "doctype": "GP Artwork Task",
            "title": task_title,
            "project": project.name,
            "description": "This is a backend test task to verify the system works",
            "priority": "High"
        })
        task.insert(ignore_permissions=True)
        print(f"✓ Created artwork task: {task.name}")
        
        # Test status history
        if len(task.status_history) > 0:
            print("✓ Status history created")
        else:
            print("✗ Status history not created")
            
        return task.name
    else:
        task = frappe.get_doc("GP Artwork Task", {"title": task_title})
        print(f"✓ Artwork task already exists: {task.name}")
        return task.name
    
    # Test 5: Test status transitions
    print("\n5. Testing Status Transitions...")
    
    try:
        task = frappe.get_doc("GP Artwork Task", {"title": task_title})
        
        # Check allowed transitions
        allowed = task.get_status_transitions()
        print(f"✓ Allowed transitions for current user: {allowed}")
        
        # Test custom permission function
        from gameplan.gameplan.doctype.gp_artwork_task.gp_artwork_task import has_permission
        
        can_read = has_permission(task.name, frappe.session.user, "read")
        can_write = has_permission(task.name, frappe.session.user, "write")
        can_create = has_permission(None, frappe.session.user, "create")
        
        print(f"✓ Permissions - Read: {can_read}, Write: {can_write}, Create: {can_create}")
        
    except Exception as e:
        print(f"✗ Error testing transitions: {str(e)}")
    
    # Test 6: Test API endpoints
    print("\n6. Testing API Endpoints...")
    
    try:
        from gameplan.api import get_artwork_tasks, get_artwork_kanban_data
        
        # Test get_artwork_tasks
        tasks = get_artwork_tasks()
        print(f"✓ get_artwork_tasks returned {len(tasks)} tasks")
        
        # Test kanban data
        kanban_data = get_artwork_kanban_data()
        print(f"✓ get_artwork_kanban_data returned data for {len(kanban_data)} statuses")
        
    except Exception as e:
        print(f"✗ Error testing API: {str(e)}")
    
    frappe.db.commit()
    
    print("\n=== Backend Testing Complete ===")
    print(f"✓ System is ready for frontend testing!")
    print(f"✓ Access the app at: http://gameplan.localhost:8002/g")
    print(f"✓ Check artwork features at: http://gameplan.localhost:8002/g/artwork-kanban")

def execute():
    test_artwork_system()

if __name__ == "__main__":
    execute()
