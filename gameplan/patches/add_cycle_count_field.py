# Copyright (c) 2025, Frappe Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe

def execute():
	"""Add cycle_count field to existing GP Artwork Task records"""
	
	# Check if the field already exists
	if frappe.db.has_column("GP Artwork Task", "cycle_count"):
		frappe.log_error("cycle_count field already exists", "Migration Skipped")
		return
	
	# Add the column
	frappe.db.sql("""
		ALTER TABLE `tabGP Artwork Task` 
		ADD COLUMN `cycle_count` int(11) NOT NULL DEFAULT 0
	""")
	
	# Update existing records to have cycle_count = 0
	frappe.db.sql("""
		UPDATE `tabGP Artwork Task` 
		SET `cycle_count` = 0 
		WHERE `cycle_count` IS NULL
	""")
	
	frappe.db.commit()
	
	frappe.log_error("Successfully added cycle_count field to GP Artwork Task", "Migration Complete")

