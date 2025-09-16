#!/usr/bin/env python3
"""
Script to assign artwork roles to users
"""
import frappe


def assign_artwork_roles():
    """Assign artwork roles to Administrator"""
    print("=== Assigning Artwork Roles ===\n")
    
    frappe.set_user("Administrator")
    
    # Check if artwork roles exist
    artwork_roles = ['Artwork Sales Team', 'Artwork Quality Team', 'Artwork Procurement Team']
    gameplan_roles = ['Gameplan Admin', 'Gameplan Member']
    
    print("1. Checking if roles exist...")
    for role in artwork_roles + gameplan_roles:
        exists = frappe.db.exists('Role', role)
        print(f"   {role}: {'✓ exists' if exists else '✗ missing'}")
        
        if not exists:
            print(f"   Creating role: {role}")
            role_doc = frappe.new_doc('Role')
            role_doc.role_name = role
            role_doc.insert()
            print(f"   ✓ Created {role}")
    
    print("\n2. Current Administrator roles...")
    admin_roles = frappe.get_roles('Administrator')
    print(f"   Administrator has: {admin_roles}")
    
    print("\n3. Adding missing artwork roles to Administrator...")
    user_doc = frappe.get_doc('User', 'Administrator')
    
    for role in artwork_roles:
        if role not in admin_roles:
            try:
                user_doc.append('roles', {'role': role})
                print(f"   ✓ Adding {role}")
            except Exception as e:
                print(f"   ✗ Failed to add {role}: {str(e)}")
        else:
            print(f"   ✓ Administrator already has {role}")
    
    # Also add Gameplan roles if missing
    for role in gameplan_roles:
        if role not in admin_roles:
            try:
                user_doc.append('roles', {'role': role})
                print(f"   ✓ Adding {role}")
            except Exception as e:
                print(f"   ✗ Failed to add {role}: {str(e)}")
        else:
            print(f"   ✓ Administrator already has {role}")
    
    # Save the user document
    try:
        user_doc.save()
        print("\n✓ Successfully saved user roles")
    except Exception as e:
        print(f"\n✗ Failed to save user: {str(e)}")
    
    print("\n4. Final role check...")
    final_roles = frappe.get_roles('Administrator')
    print(f"   Administrator now has: {final_roles}")


def execute():
    """Main execution function"""
    assign_artwork_roles()


if __name__ == "__main__":
    execute()
