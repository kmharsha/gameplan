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
from gameplan.realtime_artwork import notify_artwork_task_update


class GPArtworkTask(HasActivity, HasReactions, HasTags, HasMentions, Document):
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
		"""Validate the artwork task before saving"""
		self.validate_status_transitions()
		self.de_duplicate_reactions()

	def before_insert(self):
		"""Set initial values before inserting"""
		self.created_by_sales = frappe.session.user
		self.last_status_change = now()
		self.last_status_changed_by = frappe.session.user

	def after_insert(self):
		"""Actions after inserting the document"""
		self.add_status_history("", self.status, "Task Created")
		self.log_activity("Task Created")
		self.send_notifications("created")
		
		# If this is a task that was moved to bucket, add special status history
		if self.status == "Bucket" and self.workflow_type == "Procurement Cycle":
			self.add_status_history("Completed", "Bucket", "Moved to Procurement Bucket")
			self.log_activity("Status Changed", data={
				"old_status": "Completed",
				"new_status": "Bucket",
				"workflow_type": "Procurement Cycle",
				"cycle_count": self.cycle_count
			})
			# Send notifications to Procurement team
			self.notify_procurement_team_bucket_task()

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
			
			# Sales Cycle stops at Completed - no auto-navigation to Bucket
			# Procurement team will manually pick up completed Sales tasks

	def validate_status_transitions(self):
		"""Validate that the status transition is allowed based on workflow type and user roles"""
		if not self.has_value_changed("status"):
			return

		old_status = self.get_doc_before_save().status if self.get_doc_before_save() else ""
		new_status = self.status
		user_roles = frappe.get_roles(frappe.session.user)
		workflow_type = self.workflow_type

		# Define allowed transitions for Sales Cycle
		sales_cycle_transitions = {
			"Sales Role": {
				"Draft": ["Quality Review"],
				"Rework": ["Quality Review"]  # After rework, back to quality review
			},
			"Quality Role": {
				"Quality Review": ["Completed", "Rework"],  # Quality can complete or send back for rework
				"Rework": ["Completed", "Rework"]  # Quality can complete or continue rework
			}
		}
		
		# Define allowed transitions for Procurement Cycle
		procurement_cycle_transitions = {
			"Procurement Role": {
				"Bucket": ["Procurement Review"],  # Procurement can pick up from bucket
				"Draft": ["Procurement Review"],
				"Procurement Review": ["Quality Review"],
				"Rework": ["Procurement Review"]  # After rework, back to procurement review
			},
			"Quality Role": {
				"Quality Review": ["Final Approved", "Rework"],  # Quality can approve or send for rework
				"Rework": ["Final Approved", "Rework"]  # Quality can approve or continue rework
			}
		}

		# Select transitions based on workflow type
		if workflow_type == "Sales Cycle":
			transitions = sales_cycle_transitions
		else:  # Procurement Cycle
			transitions = procurement_cycle_transitions

		# Check if user has permission to make this transition
		allowed = False
		for role in user_roles:
			if role in transitions:
				if old_status in transitions[role]:
					if new_status in transitions[role][old_status]:
						allowed = True
						break

		# System Manager and Gameplan Admin can make any transition
		if "System Manager" in user_roles or "Gameplan Admin" in user_roles:
			allowed = True

		if not allowed:
			frappe.throw(f"You are not allowed to change status from '{old_status}' to '{new_status}' in {workflow_type}")

	def handle_status_change(self):
		"""Handle status change logic"""
		old_status = self.get_doc_before_save().status if self.get_doc_before_save() else ""
		new_status = self.status

		# Add to status history
		self.add_status_history(old_status, new_status, "Status Changed")

		# Update specific fields based on status
		if new_status == "Final Approved":
			self.final_approved_at = now()
			self.final_approved_by = frappe.session.user
			
			# If this is a procurement task, move previous cycles to bucket
			if self.workflow_type == "Procurement Cycle" and self.sales_cycle_reference:
				self.move_previous_cycles_to_bucket()

		# Log activity
		self.log_activity("Status Changed", data={
			"old_status": old_status,
			"new_status": new_status
		})

		# Send notifications
		self.send_notifications("status_changed", old_status, new_status)
		
		# Send real-time notifications
		notify_artwork_task_update(self.name, "status_changed", {
			"old_status": old_status,
			"new_status": new_status
		})

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
			"Awaiting Quality Review": ["Artwork Quality Team"],
			"Rework": ["Artwork Sales Team"],
			"Approved by Quality": ["Artwork Procurement Team"],
			"Awaiting Final Review": ["Artwork Quality Team"],
			"Final Rework": ["Artwork Procurement Team"],
			"Final Approved": ["Artwork Sales Team", "Artwork Quality Team", "Artwork Procurement Team"]
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
							f"Task '{self.title}' in artwork '{artwork_title}' (Customer: {customer_name}) changed to {new_status}",
							"Mention"
						)

		elif event_type == "created":
			# Notify Quality team when a new task is created
			users = frappe.get_all("Has Role", 
				filters={"role": "Artwork Quality Team", "parenttype": "User"},
				fields=["parent"]
			)
			
			for user in users:
				if user.parent != frappe.session.user:
					self.create_notification(
						user.parent,
						f"New task '{self.title}' created for artwork '{artwork_title}' (Customer: {customer_name})",
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
					subject=f"Gameplan Artwork Task: {self.title}",
					message=f"""
					<p>Hello,</p>
					<p>{message}</p>
					<p><strong>Task:</strong> {self.title}</p>
					<p><strong>Current Status:</strong> {self.status}</p>
					<p><strong>Artwork:</strong> {frappe.db.get_value('GP Artwork', self.artwork, 'title') if self.artwork else 'Unknown'}</p>
					<p><strong>Customer:</strong> {frappe.db.get_value('GP Project', self.customer, 'title') if self.customer else 'Unknown'}</p>
					<p><a href="{frappe.utils.get_url()}/g/artwork-tasks/{self.name}">View Task</a></p>
					<p>Best regards,<br>Gameplan Team</p>
					""",
					now=True
				)
		except Exception as e:
			frappe.log_error(f"Error sending email notification: {str(e)}")

	@frappe.whitelist()
	def change_status(self, new_status, reason="", comments=""):
		"""Change the status of the artwork task"""
		old_status = self.status
		self.status = new_status
		
		# Add reason and comments to status history
		if reason or comments:
			# Temporarily store for status history
			self._status_change_reason = reason
			self._status_change_comments = comments
		
		self.save()
		
		# Sales Cycle stops at Completed - no auto-navigation to Bucket
		# Procurement team will manually pick up completed Sales tasks
		
		return self.reload()

	def move_to_bucket(self):
		"""Move completed Sales Cycle task to Bucket for Procurement team to pick up"""
		try:
			# Change workflow type to Procurement Cycle and status to Bucket
			self.workflow_type = "Procurement Cycle"
			self.status = "Bucket"
			
			# Increment cycle count
			self.cycle_count = (self.cycle_count or 0) + 1
			
			# Save the changes
			self.save()
			
			# Add to status history
			self.add_status_history("Completed", "Bucket", "Moved to Procurement Bucket")
			
			# Log activity
			self.log_activity("Status Changed", data={
				"old_status": "Completed",
				"new_status": "Bucket",
				"workflow_type": "Procurement Cycle",
				"cycle_count": self.cycle_count
			})
			
			# Send notifications to Procurement team
			self.notify_procurement_team_bucket_task()
			
			# Send real-time notification
			notify_artwork_task_update(self.name, "moved_to_bucket", {
				"cycle_count": self.cycle_count,
				"workflow_type": "Procurement Cycle"
			})
			
			frappe.msgprint(
				f"Task '{self.title}' has been moved to Procurement Bucket (Cycle #{self.cycle_count}).",
				title="Moved to Bucket",
				indicator="blue"
			)
			
		except Exception as e:
			frappe.log_error(f"Error moving task {self.name} to bucket: {str(e)}")
			frappe.throw(f"Failed to move task to bucket: {str(e)}")

	def move_previous_cycles_to_bucket(self):
		"""Move all previous procurement cycles for the same sales task to bucket"""
		try:
			# Get all procurement tasks for the same sales task with lower cycle count
			previous_cycles = frappe.get_all("GP Artwork Task", 
				filters={
					"sales_cycle_reference": self.sales_cycle_reference,
					"workflow_type": "Procurement Cycle",
					"cycle_count": ["<", self.cycle_count],
					"status": ["!=", "Bucket"]  # Don't move tasks already in bucket
				},
				fields=["name", "title", "cycle_count"]
			)
			
			for cycle in previous_cycles:
				try:
					# Get the task document
					task_doc = frappe.get_doc("GP Artwork Task", cycle.name)
					
					# Move to bucket
					task_doc.status = "Bucket"
					task_doc.last_status_change = now()
					task_doc.last_status_changed_by = frappe.session.user
					
					# Add to status history
					task_doc.add_status_history(task_doc.status, "Bucket", f"Moved to bucket when Cycle #{self.cycle_count} was approved")
					
					# Save the document
					task_doc.save()
					
					# Log activity
					task_doc.log_activity("Task Updated", data={
						"action": "moved_to_bucket_on_approval",
						"approved_cycle": self.cycle_count,
						"moved_by": frappe.session.user
					})
					
					frappe.log_error(f"Moved Cycle #{cycle.cycle_count} to bucket when Cycle #{self.cycle_count} was approved", "Cycle Management")
					
				except Exception as e:
					frappe.log_error(f"Error moving cycle {cycle.name} to bucket: {str(e)}")
					continue
					
		except Exception as e:
			frappe.log_error(f"Error in move_previous_cycles_to_bucket: {str(e)}")

	def create_procurement_task(self):
		"""Create a new Procurement Cycle task when Sales Cycle is completed"""
		try:
			# Check if a Procurement task already exists for this Sales task
			existing_procurement_task = frappe.db.exists("GP Artwork Task", {
				"sales_cycle_reference": self.name,
				"workflow_type": "Procurement Cycle"
			})
			
			if existing_procurement_task:
				frappe.log_error(f"Procurement task already exists for Sales task {self.name}: {existing_procurement_task}")
				return
			
			# Create new Procurement Cycle task
			procurement_task = frappe.new_doc("GP Artwork Task")
			procurement_task.title = f"{self.title} - Procurement"
			procurement_task.artwork = self.artwork
			procurement_task.customer = self.customer
			procurement_task.description = self.description
			procurement_task.priority = self.priority
			procurement_task.workflow_type = "Procurement Cycle"
			procurement_task.status = "Draft"
			procurement_task.sales_cycle_reference = self.name  # Link back to sales task
			
			# Copy any relevant attachments or data
			if hasattr(self, 'attachments') and self.attachments:
				for attachment in self.attachments:
					procurement_task.append("attachments", {
						"file_name": attachment.file_name,
						"file_url": attachment.file_url,
						"version": attachment.version,
						"description": f"From Sales Task: {attachment.description}",
						"uploaded_by": frappe.session.user,
						"upload_date": now()
					})
			
			procurement_task.insert(ignore_permissions=True)
			
			# Log as a general task update since "Procurement Task Created" is not in allowed activities
			self.log_activity("Task Updated", data={
				"procurement_task": procurement_task.name,
				"procurement_task_title": procurement_task.title,
				"action": "procurement_task_created"
			})
			
			# Send notifications to Procurement team
			self.notify_procurement_team_task_created(procurement_task)
			
			# Send real-time notification
			notify_artwork_task_update(self.name, "procurement_task_created", {
				"procurement_task_id": procurement_task.name,
				"procurement_task_title": procurement_task.title
			})
			
			frappe.msgprint(
				f"Procurement task '{procurement_task.title}' has been automatically created.",
				title="Procurement Task Created",
				indicator="green"
			)
			
			return procurement_task
			
		except Exception as e:
			frappe.log_error(f"Error creating procurement task for {self.name}: {str(e)}")
			frappe.throw(f"Failed to create procurement task: {str(e)}")

	def notify_procurement_team_task_created(self, procurement_task):
		"""Notify procurement team about the new task"""
		try:
			# Get artwork and customer info for better notifications
			artwork_title = frappe.db.get_value("GP Artwork", self.artwork, "title") if self.artwork else "Unknown"
			customer_name = frappe.db.get_value("GP Project", self.customer, "title") if self.customer else "Unknown"
			
			# Notify Procurement Role users
			users = frappe.get_all("Has Role", 
				filters={"role": "Procurement Role", "parenttype": "User"},
				fields=["parent"]
			)
			
			for user in users:
				if user.parent != frappe.session.user:
					# Use "Mention" as the notification type since it's the closest valid type
					self.create_notification(
						user.parent,
						f"New procurement task '{procurement_task.title}' created from completed sales task for artwork '{artwork_title}' (Customer: {customer_name})",
						"Mention"
					)
					
		except Exception as e:
			frappe.log_error(f"Error sending procurement task notifications: {str(e)}")

	def notify_procurement_team_bucket_task(self):
		"""Notify procurement team about task moved to bucket"""
		try:
			# Get artwork and customer info for better notifications
			artwork_title = frappe.db.get_value("GP Artwork", self.artwork, "title") if self.artwork else "Unknown"
			customer_name = frappe.db.get_value("GP Project", self.customer, "title") if self.customer else "Unknown"
			
			# Notify Procurement Role users
			users = frappe.get_all("Has Role", 
				filters={"role": "Procurement Role", "parenttype": "User"},
				fields=["parent"]
			)
			
			for user in users:
				if user.parent != frappe.session.user:
					self.create_notification(
						user.parent,
						f"Task '{self.title}' moved to Procurement Bucket (Cycle #{self.cycle_count}) for artwork '{artwork_title}' (Customer: {customer_name})",
						"Mention"
					)
					
		except Exception as e:
			frappe.log_error(f"Error sending bucket task notifications: {str(e)}")

	@frappe.whitelist()
	def move_from_bucket(self, new_status="Procurement Review"):
		"""Move task from Bucket to active procurement workflow"""
		if self.status != "Bucket" or self.workflow_type != "Procurement Cycle":
			frappe.throw("This task is not in the Bucket status")
		
		old_status = self.status
		self.status = new_status
		
		# Add to status history
		self.add_status_history(old_status, new_status, "Picked up from Bucket")
		
		# Log activity
		self.log_activity("Status Changed", data={
			"old_status": old_status,
			"new_status": new_status,
			"cycle_count": self.cycle_count
		})
		
		# Send real-time notification
		notify_artwork_task_update(self.name, "moved_from_bucket", {
			"new_status": new_status,
			"cycle_count": self.cycle_count
		})
		
		frappe.msgprint(
			f"Task '{self.title}' has been moved from Bucket to {new_status} (Cycle #{self.cycle_count}).",
			title="Moved from Bucket",
			indicator="green"
		)
		
		return self.reload()

	@frappe.whitelist()
	def get_related_procurement_task(self):
		"""Get the related procurement task if this is a sales cycle task"""
		if self.workflow_type != "Sales Cycle":
			return None
			
		procurement_task = frappe.db.get_value("GP Artwork Task", {
			"sales_cycle_reference": self.name,
			"workflow_type": "Procurement Cycle"
		}, ["name", "title", "status"], as_dict=True)
		
		return procurement_task

	@frappe.whitelist()
	def get_related_sales_task(self):
		"""Get the related sales task if this is a procurement cycle task"""
		if self.workflow_type != "Procurement Cycle" or not self.sales_cycle_reference:
			return None
			
		sales_task = frappe.db.get_value("GP Artwork Task", self.sales_cycle_reference, 
			["name", "title", "status"], as_dict=True)
		
		return sales_task

	@frappe.whitelist()
	def add_attachment(self, file_url, file_name, version="1.0", description=""):
		"""Add an attachment to the artwork task"""
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
		
		# Send real-time notification
		notify_artwork_task_update(self.name, "attachment_added", {
			"file_name": file_name
		})
		
		return self.reload()

	@frappe.whitelist()
	def get_status_transitions(self):
		"""Get allowed status transitions for current user based on workflow type"""
		user_roles = frappe.get_roles(frappe.session.user)
		current_status = self.status
		workflow_type = self.workflow_type
		
		# Define allowed transitions for Sales Cycle
		sales_cycle_transitions = {
			"Sales Role": {
				"Draft": ["Quality Review"],
				"Rework": ["Quality Review"]  # After rework, back to quality review
			},
			"Quality Role": {
				"Quality Review": ["Completed", "Rework"],  # Quality can complete or send back for rework
				"Rework": ["Completed", "Rework"]  # Quality can complete or continue rework
			}
		}
		
		# Define allowed transitions for Procurement Cycle
		procurement_cycle_transitions = {
			"Procurement Role": {
				"Bucket": ["Procurement Review"],  # Procurement can pick up from bucket
				"Draft": ["Procurement Review"],
				"Procurement Review": ["Quality Review"],
				"Rework": ["Procurement Review"]  # After rework, back to procurement review
			},
			"Quality Role": {
				"Quality Review": ["Final Approved", "Rework"],  # Quality can approve or send for rework
				"Rework": ["Final Approved", "Rework"]  # Quality can approve or continue rework
			}
		}

		# Select transitions based on workflow type
		if workflow_type == "Sales Cycle":
			transitions = sales_cycle_transitions
		else:
			transitions = procurement_cycle_transitions

		allowed_statuses = []
		
		# System Manager and Gameplan Admin can transition to any status based on current status and workflow
		if "System Manager" in user_roles or "Gameplan Admin" in user_roles:
			if workflow_type == "Sales Cycle":
				# Define allowed transitions for Sales Cycle admins
				sales_admin_transitions = {
					"Draft": ["Quality Review"],
					"Quality Review": ["Completed", "Rework"],
					"Rework": ["Quality Review", "Completed"],
					"Completed": []  # Final status, no further transitions
				}
				allowed_statuses = sales_admin_transitions.get(current_status, [])
			else:
				# Define allowed transitions for Procurement Cycle admins
				procurement_admin_transitions = {
					"Bucket": ["Draft", "Procurement Review"],
					"Draft": ["Procurement Review"],
					"Procurement Review": ["Final Approved", "Rework"],
					"Rework": ["Procurement Review", "Final Approved"],
					"Final Approved": []  # Final status, no further transitions
				}
				allowed_statuses = procurement_admin_transitions.get(current_status, [])
		else:
			for role in user_roles:
				if role in transitions and current_status in transitions[role]:
					allowed_statuses.extend(transitions[role][current_status])
		
		return list(set(allowed_statuses))

	def get_user_role(self, user=None):
		"""Get the user's artwork-related role"""
		if not user:
			user = frappe.session.user
			
		user_roles = frappe.get_roles(user)
		artwork_roles = ["Artwork Sales Team", "Artwork Quality Team", "Artwork Procurement Team"]
		
		for role in artwork_roles:
			if role in user_roles:
				return role
		
		if "System Manager" in user_roles or "Gameplan Admin" in user_roles:
			return "Admin"
		
		return None


def has_permission(doc, user=None, permission_type=None):
	"""Custom permission logic for GP Artwork Task with role-based workflow filtering"""
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
	
	# Get document if needed
	if isinstance(doc, str):
		try:
			doc = frappe.get_doc("GP Artwork Task", doc)
		except:
			return False
	
	# Role-based access control based on workflow_type
	if doc and hasattr(doc, 'workflow_type'):
		workflow_type = doc.workflow_type
		
		# For read permission, allow all artwork roles to view all workflow types
		if permission_type == "read":
			# All artwork roles can read all workflow types
			pass
		else:
			# For write/create permissions, apply workflow restrictions
			# Sales Role: Only access Sales Cycle tasks for write/create
			if "Sales Role" in user_roles and workflow_type != "Sales Cycle":
				return False
				
			# Procurement Role: Only access Procurement Cycle tasks for write/create
			if "Procurement Role" in user_roles and workflow_type != "Procurement Cycle":
				return False
				
			# Quality Role: Can access both workflows (no restriction)
	
	# For create permission, both Sales and Procurement can create (in their respective cycles)
	if permission_type == "create":
		return "Sales Role" in user_roles or "Procurement Role" in user_roles
	
	# For write permission, check specific conditions
	if permission_type == "write" and doc:
		workflow_type = getattr(doc, 'workflow_type', 'Sales Cycle')
		status = getattr(doc, 'status', 'Draft')
		
		# Sales role can edit Sales Cycle tasks in specific statuses
		if "Sales Role" in user_roles:
			return (workflow_type == "Sales Cycle" and 
					status in ["Draft", "Rework"])
		
		# Procurement role can edit Procurement Cycle tasks in specific statuses
		if "Procurement Role" in user_roles:
			return (workflow_type == "Procurement Cycle" and 
					status in ["Draft", "Procurement Review", "Rework"])
		
		# Quality role can edit tasks in review stages of both workflows
		if "Quality Role" in user_roles:
			return status in ["Quality Review", "Rework", "Final Approved"]
	
	# For read permission, respect workflow_type restrictions
	return True


def on_doctype_update():
	"""Add database indexes"""
	frappe.db.add_index("GP Artwork Task", ["customer", "status"])
	frappe.db.add_index("GP Artwork Task", ["status", "modified"])
