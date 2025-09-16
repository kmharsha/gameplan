#!/usr/bin/env python3
"""
Migration script to move data from unified GP Artwork Task to separate GP Sales Task and GP Procurement Task doctypes
"""

import frappe
from frappe.utils import now

def migrate_artwork_tasks_to_separate_doctypes():
    """Migrate existing GP Artwork Task records to appropriate separate doctypes"""
    
    print("Starting migration from GP Artwork Task to separate doctypes...")
    
    # Get all existing GP Artwork Task records
    artwork_tasks = frappe.get_all("GP Artwork Task", 
        fields=["name", "title", "artwork", "customer", "workflow_type", "status", 
                "description", "assigned_to", "priority", "sales_cycle_reference", 
                "cycle_count", "created_by_sales", "last_status_change", 
                "last_status_changed_by", "final_approved_at", "final_approved_by"],
        order_by="creation asc"
    )
    
    print(f"Found {len(artwork_tasks)} GP Artwork Task records to migrate")
    
    sales_tasks_created = 0
    procurement_tasks_created = 0
    errors = []
    
    for task in artwork_tasks:
        try:
            if task.workflow_type == "Sales Cycle":
                # Create GP Sales Task
                sales_task = create_sales_task(task)
                sales_tasks_created += 1
                print(f"Created Sales Task: {sales_task.name} - {sales_task.title}")
                
            elif task.workflow_type == "Procurement Cycle":
                # Create GP Procurement Task
                procurement_task = create_procurement_task(task)
                procurement_tasks_created += 1
                print(f"Created Procurement Task: {procurement_task.name} - {procurement_task.title}")
                
        except Exception as e:
            error_msg = f"Error migrating task {task.name}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)
            frappe.log_error(error_msg, "Migration Error")
    
    print(f"\nMigration completed!")
    print(f"Sales Tasks created: {sales_tasks_created}")
    print(f"Procurement Tasks created: {procurement_tasks_created}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"  - {error}")
    
    return {
        "sales_tasks_created": sales_tasks_created,
        "procurement_tasks_created": procurement_tasks_created,
        "errors": errors
    }

def create_sales_task(artwork_task):
    """Create a GP Sales Task from GP Artwork Task"""
    
    # Create the sales task
    sales_task = frappe.new_doc("GP Sales Task")
    sales_task.title = artwork_task.title
    sales_task.artwork = artwork_task.artwork
    sales_task.customer = artwork_task.customer
    sales_task.status = artwork_task.status
    sales_task.description = artwork_task.description or ""
    sales_task.assigned_to = artwork_task.assigned_to
    sales_task.priority = artwork_task.priority or "Medium"
    sales_task.created_by_sales = artwork_task.created_by_sales
    sales_task.last_status_change = artwork_task.last_status_change
    sales_task.last_status_changed_by = artwork_task.last_status_changed_by
    
    # Set quality approval fields if status is Completed
    if artwork_task.status == "Completed":
        sales_task.approved_by_quality_at = artwork_task.final_approved_at
        sales_task.approved_by_quality_by = artwork_task.final_approved_by
    
    # Copy attachments
    copy_attachments(artwork_task.name, sales_task, "GP Sales Task")
    
    # Copy status history
    copy_status_history(artwork_task.name, sales_task, "GP Sales Task")
    
    # Copy reactions and tags
    copy_reactions_and_tags(artwork_task.name, sales_task, "GP Sales Task")
    
    sales_task.insert(ignore_permissions=True)
    return sales_task

def create_procurement_task(artwork_task):
    """Create a GP Procurement Task from GP Artwork Task"""
    
    # Create the procurement task
    procurement_task = frappe.new_doc("GP Procurement Task")
    procurement_task.title = artwork_task.title
    procurement_task.artwork = artwork_task.artwork
    procurement_task.customer = artwork_task.customer
    procurement_task.status = artwork_task.status
    procurement_task.description = artwork_task.description or ""
    procurement_task.assigned_to = artwork_task.assigned_to
    procurement_task.priority = artwork_task.priority or "Medium"
    procurement_task.sales_task_reference = artwork_task.sales_cycle_reference
    procurement_task.created_by_procurement = artwork_task.created_by_sales  # Will be updated later
    procurement_task.last_status_change = artwork_task.last_status_change
    procurement_task.last_status_changed_by = artwork_task.last_status_changed_by
    procurement_task.final_approved_at = artwork_task.final_approved_at
    procurement_task.final_approved_by = artwork_task.final_approved_by
    
    # Copy attachments
    copy_attachments(artwork_task.name, procurement_task, "GP Procurement Task")
    
    # Copy status history
    copy_status_history(artwork_task.name, procurement_task, "GP Procurement Task")
    
    # Copy reactions and tags
    copy_reactions_and_tags(artwork_task.name, procurement_task, "GP Procurement Task")
    
    procurement_task.insert(ignore_permissions=True)
    return procurement_task

def copy_attachments(source_task_name, target_doc, target_doctype):
    """Copy attachments from source task to target document"""
    try:
        source_attachments = frappe.get_all("GP Artwork Attachment",
            filters={"parent": source_task_name},
            fields=["file_name", "file_url", "version", "description", "uploaded_by", "upload_date"]
        )
        
        for attachment in source_attachments:
            target_doc.append("attachments", {
                "file_name": attachment.file_name,
                "file_url": attachment.file_url,
                "version": attachment.version,
                "description": attachment.description,
                "uploaded_by": attachment.uploaded_by,
                "upload_date": attachment.upload_date
            })
    except Exception as e:
        print(f"Warning: Could not copy attachments for {source_task_name}: {str(e)}")

def copy_status_history(source_task_name, target_doc, target_doctype):
    """Copy status history from source task to target document"""
    try:
        source_history = frappe.get_all("GP Artwork Status History",
            filters={"parent": source_task_name},
            fields=["from_status", "to_status", "changed_by", "change_date", "reason", "comments"],
            order_by="change_date asc"
        )
        
        for history_item in source_history:
            target_doc.append("status_history", {
                "from_status": history_item.from_status,
                "to_status": history_item.to_status,
                "changed_by": history_item.changed_by,
                "change_date": history_item.change_date,
                "reason": history_item.reason or "",
                "comments": history_item.comments or ""
            })
    except Exception as e:
        print(f"Warning: Could not copy status history for {source_task_name}: {str(e)}")

def copy_reactions_and_tags(source_task_name, target_doc, target_doctype):
    """Copy reactions and tags from source task to target document"""
    try:
        # Copy reactions
        source_reactions = frappe.get_all("GP Reaction",
            filters={"parent": source_task_name},
            fields=["user", "reaction", "creation"]
        )
        
        for reaction in source_reactions:
            target_doc.append("reactions", {
                "user": reaction.user,
                "reaction": reaction.reaction,
                "creation": reaction.creation
            })
        
        # Copy tags
        source_tags = frappe.get_all("GP Tag Link",
            filters={"parent": source_task_name},
            fields=["tag"]
        )
        
        for tag in source_tags:
            target_doc.append("tags", {
                "tag": tag.tag
            })
    except Exception as e:
        print(f"Warning: Could not copy reactions and tags for {source_task_name}: {str(e)}")

def update_procurement_task_references():
    """Update sales_task_reference in procurement tasks to point to new sales task names"""
    print("Updating procurement task references to point to new sales tasks...")
    
    # Get all procurement tasks that have sales_cycle_reference
    procurement_tasks = frappe.get_all("GP Procurement Task",
        filters={"sales_task_reference": ["!=", ""]},
        fields=["name", "sales_task_reference"]
    )
    
    updated_count = 0
    
    for proc_task in procurement_tasks:
        try:
            # Find the corresponding sales task by matching title and artwork
            sales_task = frappe.get_all("GP Sales Task",
                filters={
                    "title": ["like", f"%{proc_task.sales_task_reference}%"]
                },
                fields=["name"],
                limit=1
            )
            
            if sales_task:
                # Update the reference
                frappe.db.set_value("GP Procurement Task", proc_task.name, 
                                  "sales_task_reference", sales_task[0].name)
                updated_count += 1
                print(f"Updated procurement task {proc_task.name} to reference sales task {sales_task[0].name}")
            else:
                print(f"Warning: Could not find corresponding sales task for procurement task {proc_task.name}")
                
        except Exception as e:
            print(f"Error updating procurement task {proc_task.name}: {str(e)}")
    
    print(f"Updated {updated_count} procurement task references")
    return updated_count

if __name__ == "__main__":
    # Run the migration
    frappe.init()
    frappe.connect()
    
    try:
        result = migrate_artwork_tasks_to_separate_doctypes()
        update_procurement_task_references()
        
        print("\nMigration completed successfully!")
        print(f"Sales Tasks created: {result['sales_tasks_created']}")
        print(f"Procurement Tasks created: {result['procurement_tasks_created']}")
        print(f"Errors: {len(result['errors'])}")
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        frappe.log_error(f"Migration failed: {str(e)}", "Migration Error")
    finally:
        frappe.destroy()
