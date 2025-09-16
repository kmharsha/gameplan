# Copyright (c) 2025, Frappe Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, get_fullname

from gameplan.mixins.activity import HasActivity
# from gameplan.mixins.reactions import HasReactions  # Removed - artworks don't need reactions
from gameplan.mixins.tags import HasTags
from gameplan.mixins.mentions import HasMentions


class GPArtwork(HasActivity, HasTags, HasMentions, Document):
	# Class Configuration
	on_delete_cascade = ["GP Comment", "GP Activity", "GP Artwork Task"]
	on_delete_set_null = ["GP Notification"]
	activities = [
		"Artwork Created",
		"Artwork Updated", 
		"Status Changed",
		"Task Added"
	]
	tags_field = "description"
	mentions_field = "description"

	def validate(self):
		"""Validate the artwork before saving"""
		self.validate_dates()
		# self.de_duplicate_reactions()  # Removed - artworks don't have reactions field

	def before_insert(self):
		"""Set initial values before inserting"""
		self.created_by_sales = frappe.session.user
		self.creation_date = now()
		self.last_updated_by = frappe.session.user
		self.last_updated = now()

	def after_insert(self):
		"""Actions after inserting the document"""
		self.log_activity("Artwork Created")
		self.send_notifications("created")

	def on_update(self):
		"""Actions on document update"""
		self.notify_mentions()
		# self.notify_reactions()  # Removed - artworks don't have reactions field
		self.update_tags()
		
		# Update tracking fields
		self.last_updated_by = frappe.session.user
		self.last_updated = now()
		
		if self.has_value_changed("status"):
			self.handle_status_change()

	def validate_dates(self):
		"""Validate that due date is after start date"""
		if self.start_date and self.due_date:
			if self.due_date < self.start_date:
				frappe.throw("Due date cannot be before start date")

	def handle_status_change(self):
		"""Handle status change logic"""
		old_status = self.get_doc_before_save().status if self.get_doc_before_save() else ""
		new_status = self.status

		# Log activity
		self.log_activity("Status Changed", data={
			"old_status": old_status,
			"new_status": new_status
		})

		# Send notifications
		self.send_notifications("status_changed", old_status, new_status)

	def send_notifications(self, event_type, old_status=None, new_status=None):
		"""Send notifications based on the event"""
		# Get all users who should be notified for this customer's artwork
		notification_roles = ["Artwork Sales Team", "Artwork Quality Team", "Artwork Procurement Team"]
		
		for role in notification_roles:
			users = frappe.get_all("Has Role", 
				filters={"role": role, "parenttype": "User"},
				fields=["parent"]
			)
			
			for user in users:
				if user.parent != frappe.session.user:  # Don't notify the user who made the change
					if event_type == "created":
						message = f"New artwork '{self.title}' has been created for customer {self.customer}"
					elif event_type == "status_changed":
						message = f"Artwork '{self.title}' status changed from {old_status} to {new_status}"
					else:
						message = f"Artwork '{self.title}' has been updated"
					
					self.create_notification(
						user.parent,
						message,
						event_type
					)

	def create_notification(self, user, message, notification_type):
		"""Create a notification for a user"""
		try:
			notification = frappe.new_doc("GP Notification")
			notification.to_user = user
			notification.from_user = frappe.session.user
			notification.type = notification_type
			notification.message = message
			notification.reference_doctype = self.doctype
			notification.reference_name = self.name
			notification.insert(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(f"Error creating notification: {str(e)}")

	@frappe.whitelist()
	def get_artwork_tasks(self):
		"""Get all tasks for this artwork"""
		return frappe.get_all("GP Artwork Task",
			filters={"artwork": self.name},
			fields=["name", "title", "status", "priority", "assigned_to", "modified"],
			order_by="creation desc"
		)

	@frappe.whitelist()
	def create_artwork_task(self, title, description="", priority="Medium", assigned_to=None):
		"""Create a new task for this artwork"""
		task = frappe.new_doc("GP Artwork Task")
		task.title = title
		task.description = description
		task.artwork = self.name
		task.customer = self.customer  # Inherit customer from artwork
		task.priority = priority
		if assigned_to:
			task.assigned_to = assigned_to
		
		task.insert()
		
		# Log activity on the artwork
		self.log_activity("Task Added", data={"task_name": task.name, "task_title": title})
		
		return task

	def get_progress_summary(self):
		"""Get progress summary of all tasks for this artwork"""
		tasks = frappe.get_all("GP Artwork Task",
			filters={"artwork": self.name},
			fields=["status"],
		)
		
		if not tasks:
			return {"total": 0, "completed": 0, "in_progress": 0, "draft": 0}
		
		summary = {"total": len(tasks), "completed": 0, "in_progress": 0, "draft": 0}
		
		for task in tasks:
			if task.status == "Final Approved":
				summary["completed"] += 1
			elif task.status in ["Awaiting Quality Review", "Approved by Quality", "Awaiting Final Review"]:
				summary["in_progress"] += 1
			elif task.status in ["Draft", "Rework", "Final Rework"]:
				summary["draft"] += 1
		
		return summary


def has_permission(doc, user=None, permission_type=None):
	"""Custom permission logic for GP Artwork"""
	if not user:
		user = frappe.session.user

	if user == "Administrator":
		return True

	user_roles = frappe.get_roles(user)

	# System Manager and Gameplan Admin have full access
	if "System Manager" in user_roles or "Gameplan Admin" in user_roles:
		return True

	# Check if user has any artwork-related role
	artwork_roles = ["Artwork Sales Team", "Artwork Quality Team", "Artwork Procurement Team"]
	has_artwork_role = any(role in user_roles for role in artwork_roles)

	if not has_artwork_role:
		return False

	# For create permission, only Sales Team can create
	if permission_type == "create":
		return "Artwork Sales Team" in user_roles

	# For write permission, only Sales Team can edit (and only their own artworks)
	if permission_type == "write":
		if isinstance(doc, str):
			doc = frappe.get_doc("GP Artwork", doc)
		
		# Sales team can edit their own artworks
		if "Artwork Sales Team" in user_roles:
			return doc.created_by_sales == user
		
		# Other teams can only read
		return False

	# For read permission, all artwork roles can read
	return True


def on_doctype_update():
	"""Add database indexes"""
	frappe.db.add_index("GP Artwork", ["customer", "status"])
	frappe.db.add_index("GP Artwork", ["status", "modified"])
