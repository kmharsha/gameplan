# Copyright (c) 2025, Frappe Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, get_fullname

from gameplan.gameplan.doctype.gp_notification.gp_notification import GPNotification
from gameplan.mixins.activity import HasActivity
from gameplan.mixins.reactions import HasReactions
from gameplan.mixins.tags import HasTags
from gameplan.mixins.mentions import HasMentions


class GPProcurementTask(HasActivity, HasReactions, HasTags, HasMentions, Document):
	# Class Configuration
	on_delete_cascade = ["GP Comment", "GP Activity"]
	on_delete_set_null = ["GP Notification"]
	activities = [
		"Status Changed",
		"Task Created",
		"Task Updated",
		"Attachment Added",
	]
	tags_field = "description"
	mentions_field = "description"

	def validate(self):
		"""Validate the procurement task before saving"""
		self.validate_status_transitions()
		self.de_duplicate_reactions()

	def before_insert(self):
		"""Set initial values before inserting"""
		self.created_by_procurement = frappe.session.user
		self.last_status_change = now()
		self.last_status_changed_by = frappe.session.user

	def after_insert(self):
		"""Actions after inserting the document"""
		self.add_status_history("", self.status, "Task Created")
		self.log_activity("Task Created")
		self.send_notifications("created")

	def on_update(self):
		"""Actions on document update"""
		self.notify_mentions()
		self.notify_reactions()
		self.update_tags()
		
		if self.has_value_changed("status"):
			self.handle_status_change()

	def before_save(self):
		"""Actions before saving"""
		# Update last status change info if status changed
		if self.has_value_changed("status"):
			self.last_status_change = now()
			self.last_status_changed_by = frappe.session.user

	def validate_status_transitions(self):
		"""Validate that the status transition is allowed based on user roles"""
		if not self.has_value_changed("status"):
			return

		old_status = self.get_doc_before_save().status if self.get_doc_before_save() else ""
		new_status = self.status
		user_roles = frappe.get_roles(frappe.session.user)

		# Define allowed transitions for Procurement Cycle
		procurement_cycle_transitions = {
			"Procurement Role": {
				"Bucket": ["Procurement Draft", "Procurement Review"],  # Can move from bucket to draft or procurement review
				"Procurement Draft": ["Procurement Review"],
				"Procurement Review": ["Final Approved", "Procurement Rework"],  # Procurement can approve or send for rework
				"Procurement Rework": ["Procurement Review", "Final Approved"]  # After rework, back to procurement review or approve
			}
		}

		# Check if user has permission to make this transition
		allowed = False
		for role in user_roles:
			if role in procurement_cycle_transitions:
				if old_status in procurement_cycle_transitions[role]:
					if new_status in procurement_cycle_transitions[role][old_status]:
						allowed = True
						break

		# System Manager and Gameplan Admin can make any transition
		if "System Manager" in user_roles or "Gameplan Admin" in user_roles:
			allowed = True

		if not allowed:
			frappe.throw(f"You are not allowed to change status from '{old_status}' to '{new_status}' in Procurement Cycle")

	def handle_status_change(self):
		"""Handle status change logic"""
		old_status = self.get_doc_before_save().status if self.get_doc_before_save() else ""
		new_status = self.status

		# Add to status history
		self.add_status_history(old_status, new_status, "Status Changed")

		# Update specific fields based on status
		if new_status == "Completed":
			self.final_approved_at = now()
			self.final_approved_by = frappe.session.user

		# Log activity
		self.log_activity("Status Changed", data={
			"old_status": old_status,
			"new_status": new_status
		})

		# Send notifications
		self.send_notifications("status_changed", old_status, new_status)

	def add_status_history(self, from_status, to_status, reason="", comments=""):
		"""Add an entry to status history"""
		self.append("status_history", {
			"from_status": from_status,
			"to_status": to_status,
			"changed_by": frappe.session.user,
			"change_date": now(),
			"reason": reason,
			"comments": comments
		})

	def send_notifications(self, event_type, old_status=None, new_status=None):
		"""Send notifications based on the event"""
		# Get artwork and customer info for better notifications
		artwork_title = frappe.db.get_value("GP Artwork", self.artwork, "title") if self.artwork else "Unknown"
		customer_name = frappe.db.get_value("GP Project", self.customer, "title") if self.customer else "Unknown"
		
		# Define who should be notified for each status
		notification_map = {
			"Procurement Review": ["Procurement Role"],
			"Rework": ["Procurement Role"],
			"Completed": ["Procurement Role"]
		}

		if event_type == "status_changed" and new_status:
			roles_to_notify = notification_map.get(new_status, [])
			
			for role in roles_to_notify:
				users = frappe.get_all("Has Role", 
					filters={"role": role, "parenttype": "User"},
					fields=["parent"]
				)
				
				for user in users:
					if user.parent != frappe.session.user:  # Don't notify the user who made the change
						self.create_notification(
							user.parent,
							f"Procurement Task '{self.title}' in artwork '{artwork_title}' (Customer: {customer_name}) changed to {new_status}",
							"Mention"
						)

		elif event_type == "created":
			# Notify Quality team when a new procurement task is created
			users = frappe.get_all("Has Role", 
				filters={"role": "Quality Role", "parenttype": "User"},
				fields=["parent"]
			)
			
			for user in users:
				if user.parent != frappe.session.user:
					self.create_notification(
						user.parent,
						f"New procurement task '{self.title}' created for artwork '{artwork_title}' (Customer: {customer_name})",
						"Mention"
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
			
			# Also send email notification
			self.send_email_notification(user, message)
			
		except Exception as e:
			frappe.log_error(f"Error creating notification: {str(e)}")

	def send_email_notification(self, user, message):
		"""Send email notification to user"""
		try:
			user_email = frappe.db.get_value("User", user, "email")
			if user_email:
				frappe.sendmail(
					recipients=[user_email],
					subject=f"Gameplan Procurement Task: {self.title}",
					message=f"""
					<p>Hello,</p>
					<p>{message}</p>
					<p><strong>Task:</strong> {self.title}</p>
					<p><strong>Current Status:</strong> {self.status}</p>
					<p><strong>Artwork:</strong> {frappe.db.get_value('GP Artwork', self.artwork, 'title') if self.artwork else 'Unknown'}</p>
					<p><strong>Customer:</strong> {frappe.db.get_value('GP Project', self.customer, 'title') if self.customer else 'Unknown'}</p>
					<p><a href="{frappe.utils.get_url()}/g/procurement-tasks/{self.name}">View Task</a></p>
					<p>Best regards,<br>Gameplan Team</p>
					""",
					now=True
				)
		except Exception as e:
			frappe.log_error(f"Error sending email notification: {str(e)}")

	@frappe.whitelist()
	def change_status(self, new_status, reason="", comments=""):
		"""Change the status of the procurement task"""
		old_status = self.status
		self.status = new_status
		
		# Add reason and comments to status history
		if reason or comments:
			# Temporarily store for status history
			self._status_change_reason = reason
			self._status_change_comments = comments
		
		self.save()
		return self.reload()

	@frappe.whitelist()
	def get_status_transitions(self):
		"""Get allowed status transitions for current user"""
		user_roles = frappe.get_roles(frappe.session.user)
		current_status = self.status
		
		# Define allowed transitions for Procurement Cycle
		procurement_cycle_transitions = {
			"Procurement Role": {
				"Bucket": ["Procurement Draft", "Procurement Review"],  # Can move from bucket to draft or procurement review
				"Procurement Draft": ["Procurement Review"],
				"Procurement Review": ["Final Approved", "Procurement Rework"],  # Procurement can approve or send for rework
				"Procurement Rework": ["Procurement Review", "Final Approved"]  # After rework, back to procurement review or approve
			}
		}

		allowed_statuses = []
		
		# System Manager and Gameplan Admin can transition to any status based on current status
		if "System Manager" in user_roles or "Gameplan Admin" in user_roles:
			# Define allowed transitions for admins based on current status
			admin_transitions = {
				"Bucket": ["Procurement Draft", "Procurement Review"],
				"Procurement Draft": ["Procurement Review"],
				"Procurement Review": ["Final Approved", "Procurement Rework"],
				"Procurement Rework": ["Procurement Review", "Final Approved"],
				"Final Approved": []  # Final status, no further transitions
			}
			allowed_statuses = admin_transitions.get(current_status, [])
		else:
			for role in user_roles:
				if role in procurement_cycle_transitions and current_status in procurement_cycle_transitions[role]:
					allowed_statuses.extend(procurement_cycle_transitions[role][current_status])
		
		return list(set(allowed_statuses))

	@frappe.whitelist()
	def add_attachment(self, file_url, file_name, version="1.0", description=""):
		"""Add an attachment to the procurement task"""
		self.append("attachments", {
			"file_name": file_name,
			"file_url": file_url,
			"version": version,
			"uploaded_by": frappe.session.user,
			"upload_date": now(),
			"description": description
		})
		
		self.save()
		self.log_activity("Attachment Added", data={"file_name": file_name})
		
		return self.reload()


def has_permission(doc, user=None, permission_type=None):
	"""Custom permission logic for GP Procurement Task"""
	if not user:
		user = frappe.session.user
	
	if user == "Administrator":
		return True
	
	user_roles = frappe.get_roles(user)
	
	# System Manager and Gameplan Admin have full access
	if "System Manager" in user_roles or "Gameplan Admin" in user_roles:
		return True
	
	# Check if user has any artwork-related role
	artwork_roles = ["Sales Role", "Procurement Role", "Quality Role"]
	has_artwork_role = any(role in user_roles for role in artwork_roles)
	
	if not has_artwork_role:
		return False
	
	# For read permission, allow all artwork roles to view
	if permission_type == "read":
		return True
	
	# For create permission, Procurement Role can create
	if permission_type == "create":
		return "Procurement Role" in user_roles
	
	# For write permission, check specific conditions
	if permission_type == "write" and doc:
		status = getattr(doc, 'status', 'Draft')
		
		# Procurement role can edit in specific statuses
		if "Procurement Role" in user_roles:
			return status in ["Draft", "Procurement Review", "Rework"]
		
		# Quality role can edit in review stages
		if "Quality Role" in user_roles:
			return status in ["Quality Review", "Rework", "Final Approved"]
	
	return True


def on_doctype_update():
	"""Add database indexes"""
	frappe.db.add_index("GP Procurement Task", ["artwork", "status"])
	frappe.db.add_index("GP Procurement Task", ["status", "modified"])
