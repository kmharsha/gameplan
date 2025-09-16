#!/usr/bin/env python3
"""
Test script to simulate frontend API calls for artwork task creation
"""
import frappe
import json


def test_create_artwork_task():
    """Test artwork task creation via API endpoint"""
    try:
        # Set up test data
        frappe.set_user("Administrator")
        
        # Get test project and team
        project = frappe.db.get_value("GP Project", {"title": "Test Project for Artwork"}, "name")
        team = frappe.db.get_value("GP Team", {"title": "Test Team"}, "name") 
        
        if not project or not team:
            print("❌ Missing test data - run artwork setup first")
            return
        
        print(f"Using project: {project}, team: {team}")
        
        # Test data that would come from frontend
        task_data = {
            "title": "Test Artwork Task from Frontend",
            "description": "This is a test artwork task created via API",
            "project": project,  # This should be a string, not an object
            "team": team,
            "status": "Draft",
            "priority": "Medium",
            "tags": ["test", "api"]
        }
        
        print(f"Creating task with data: {json.dumps(task_data, indent=2)}")
        
        # Call the API method directly
        from gameplan.api import create_artwork_task
        result = create_artwork_task(
            title=task_data["title"],
            description=task_data["description"],
            project=task_data["project"],
            team=task_data["team"],
            status=task_data["status"],
            priority=task_data["priority"],
            tags=task_data["tags"]
        )
        
        print(f"✓ Successfully created artwork task: {result['name']}")
        print(f"  Status: {result['status']}")
        print(f"  Project: {result['project']}")
        print(f"  Team: {result['team']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error creating artwork task: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_get_artwork_tasks():
    """Test getting artwork tasks list"""
    try:
        from gameplan.api import get_artwork_tasks
        
        tasks = get_artwork_tasks(limit=10)
        print(f"✓ Retrieved {len(tasks)} artwork tasks")
        
        for task in tasks[:3]:  # Show first 3
            print(f"  - {task['name']}: {task['title']} ({task['status']})")
            
        return tasks
        
    except Exception as e:
        print(f"❌ Error getting artwork tasks: {str(e)}")
        return []


def test_kanban_data():
    """Test getting kanban data"""
    try:
        from gameplan.api import get_artwork_kanban_data
        
        kanban_data = get_artwork_kanban_data()
        print(f"✓ Retrieved kanban data with {len(kanban_data)} columns")
        
        for column in kanban_data:
            print(f"  - {column['status']}: {len(column['tasks'])} tasks")
            
        return kanban_data
        
    except Exception as e:
        print(f"❌ Error getting kanban data: {str(e)}")
        return []


def execute():
    """Main test execution"""
    print("=== Testing Frontend API Calls ===\n")
    
    print("1. Testing task creation...")
    task = test_create_artwork_task()
    print()
    
    print("2. Testing task list retrieval...")
    tasks = test_get_artwork_tasks()
    print()
    
    print("3. Testing kanban data...")
    kanban = test_kanban_data()
    print()
    
    print("=== All tests completed ===")


if __name__ == "__main__":
    execute()
