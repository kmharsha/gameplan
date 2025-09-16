# Copyright (c) 2025, Frappe Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GPArtworkStatusHistory(Document):
	def before_insert(self):
		"""Set default values before inserting"""
		if not self.changed_by:
			self.changed_by = frappe.session.user
		if not self.change_date:
			self.change_date = frappe.utils.now()
