# Copyright (c) 2025, Frappe Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GPArtworkAttachment(Document):
	def before_insert(self):
		"""Set default values before inserting"""
		self.uploaded_by = frappe.session.user
		self.upload_date = frappe.utils.now()
		
		# Get file size if not set
		if self.file_url and not self.file_size:
			try:
				import os
				file_path = frappe.get_site_path("public", "files", self.file_url.split("/files/")[-1])
				if os.path.exists(file_path):
					size = os.path.getsize(file_path)
					self.file_size = self.format_file_size(size)
			except:
				pass
	
	def format_file_size(self, size_bytes):
		"""Format file size in human readable format"""
		if size_bytes == 0:
			return "0B"
		size_name = ["B", "KB", "MB", "GB", "TB"]
		i = 0
		while size_bytes >= 1024 and i < len(size_name) - 1:
			size_bytes /= 1024.0
			i += 1
		return f"{size_bytes:.1f} {size_name[i]}"
