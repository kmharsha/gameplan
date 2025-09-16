#!/usr/bin/env python3

import frappe
from frappe.core.doctype.role.role import Role

def setup_artwork_roles():
    """Create the artwork system roles"""
    roles = [
        "Artwork Sales Team",
        "Artwork Quality Team", 
        "Artwork Procurement Team"
    ]
    
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            role_doc = frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1
            })
            role_doc.insert(ignore_permissions=True)
            print(f"Created role: {role_name}")
        else:
            print(f"Role already exists: {role_name}")

def setup_test_user():
    """Create test users for each role"""
    users_data = [
        {
            "email": "sales@artwork.test",
            "first_name": "Sales",
            "last_name": "User",
            "role": "Artwork Sales Team"
        },
        {
            "email": "quality@artwork.test", 
            "first_name": "Quality",
            "last_name": "User",
            "role": "Artwork Quality Team"
        },
        {
            "email": "procurement@artwork.test",
            "first_name": "Procurement", 
            "last_name": "User",
            "role": "Artwork Procurement Team"
        }
    ]
    
    for user_data in users_data:
        if not frappe.db.exists("User", user_data["email"]):
            user_doc = frappe.get_doc({
                "doctype": "User",
                "email": user_data["email"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "enabled": 1,
                "new_password": "artwork123",
                "roles": [
                    {"role": "Gameplan Member"},
                    {"role": user_data["role"]}
                ]
            })
            user_doc.insert(ignore_permissions=True)
            print(f"Created user: {user_data['email']}")
        else:
            print(f"User already exists: {user_data['email']}")

def create_test_project():
    """Create a test project for artwork tasks"""
    project_name = "Test Artwork Project"
    
    if not frappe.db.exists("GP Project", {"title": project_name}):
        # First create a team if it doesn't exist
        team_name = "Test Team"
        if not frappe.db.exists("GP Team", {"title": team_name}):
            team_doc = frappe.get_doc({
                "doctype": "GP Team",
                "title": team_name,
                "description": "Test team for artwork system"
            })
            team_doc.insert(ignore_permissions=True)
            print(f"Created team: {team_name}")
        
        # Get team name
        team = frappe.get_doc("GP Team", {"title": team_name})
        
        # Create project
        project_doc = frappe.get_doc({
            "doctype": "GP Project", 
            "title": project_name,
            "team": team.name,
            "description": "Test project for artwork tasks"
        })
        project_doc.insert(ignore_permissions=True)
        print(f"Created project: {project_name}")
        return project_doc.name
    else:
        project = frappe.get_doc("GP Project", {"title": project_name})
        print(f"Project already exists: {project_name}")
        return project.name

def create_test_artwork_task(project_name):
    """Create a test artwork task"""
    if not frappe.db.exists("GP Artwork Task", {"title": "Test Artwork Task"}):
        task_doc = frappe.get_doc({
            "doctype": "GP Artwork Task",
            "title": "Test Artwork Task", 
            "project": project_name,
            "description": "This is a test artwork task to verify the system works",
            "priority": "Medium"
        })
        task_doc.insert(ignore_permissions=True)
        print(f"Created test artwork task: {task_doc.name}")
        return task_doc.name
    else:
        task = frappe.get_doc("GP Artwork Task", {"title": "Test Artwork Task"})
        print(f"Test artwork task already exists: {task.name}")
        return task.name

def execute():
    """Main execution function"""
    print("Setting up Artwork Management System...")
    
    setup_artwork_roles()
    setup_test_user()
    project_name = create_test_project()
    task_name = create_test_artwork_task(project_name)
    
    frappe.db.commit()
    
    print("\n=== Setup Complete ===")
    print(f"Test Project: {project_name}")
    print(f"Test Task: {task_name}")
    print("\nTest Users Created:")
    print("- sales@artwork.test (password: artwork123)")
    print("- quality@artwork.test (password: artwork123)")
    print("- procurement@artwork.test (password: artwork123)")
    print("\nYou can now test the artwork system!")

if __name__ == "__main__":
    execute()
