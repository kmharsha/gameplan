# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt


import frappe
from frappe.query_builder.functions import Count
from frappe.utils import cstr, split_emails, validate_email_address, now

import gameplan
from gameplan.utils import validate_type


@frappe.whitelist(allow_guest=True)
def get_user_info(user=None):
	if frappe.session.user == "Guest":
		frappe.throw("Authentication failed", exc=frappe.AuthenticationError)

	filters = {"roles.role": ["like", "Gameplan %"]}
	if user:
		filters["name"] = user

	users = frappe.qb.get_query(
		"User",
		filters=filters,
		fields=["name", "email", "enabled", "user_image", "full_name", "user_type"],
		order_by="full_name asc",
		distinct=True,
	).run(as_dict=1)

	# Get discussion counts for last 3 months
	Discussion = frappe.qb.DocType("GP Discussion")
	discussion_counts = (
		frappe.qb.from_(Discussion)
		.select(Discussion.owner, Count(Discussion.name).as_("count"))
		.where(Discussion.creation >= frappe.utils.add_months(frappe.utils.now(), -3))
		.where(Discussion.owner.isin([u.name for u in users]))
		.groupby(Discussion.owner)
	).run(as_dict=1)
	discussion_count_map = {d.owner: d.count for d in discussion_counts}

	# Get comment counts for last 3 months
	Comment = frappe.qb.DocType("GP Comment")
	comment_counts = (
		frappe.qb.from_(Comment)
		.select(Comment.owner, Count(Comment.name).as_("count"))
		.where(Comment.creation >= frappe.utils.add_months(frappe.utils.now(), -3))
		.where(Comment.owner.isin([u.name for u in users]))
		.groupby(Comment.owner)
	).run(as_dict=1)
	comment_count_map = {c.owner: c.count for c in comment_counts}

	roles = frappe.db.get_all("Has Role", filters={"parenttype": "User"}, fields=["role", "parent"])
	user_profiles = frappe.db.get_all(
		"GP User Profile",
		fields=["user", "name", "image", "image_background_color", "is_image_background_removed", "bio"],
		filters={"user": ["in", [u.name for u in users]]},
	)
	user_profile_map = {u.user: u for u in user_profiles}
	for user in users:
		if frappe.session.user == user.name:
			user.session_user = True
		user_profile = user_profile_map.get(user.name)
		if user_profile:
			user.user_profile = user_profile.name
			user.user_image = user_profile.image
			user.image_background_color = user_profile.image_background_color
			user.is_image_background_removed = user_profile.is_image_background_removed
			user.bio = user_profile.bio
		user_roles = [r.role for r in roles if r.parent == user.name]
		user.role = None
		for role in ["Gameplan Guest", "Gameplan Member", "Gameplan Admin"]:
			if role in user_roles:
				user.role = role

		# Add discussion and comment counts
		user.discussions_count_3m = discussion_count_map.get(user.name, 0)
		user.comments_count_3m = comment_count_map.get(user.name, 0)

	return users


@frappe.whitelist()
@validate_type
def change_user_role(user: str, role: str):
	if gameplan.is_guest():
		frappe.throw("Only Admin can change user roles")

	if role not in ["Gameplan Guest", "Gameplan Member", "Gameplan Admin"]:
		return get_user_info(user)[0]

	user_doc = frappe.get_doc("User", user)
	for _role in user_doc.roles:
		if _role.role in ["Gameplan Guest", "Gameplan Member", "Gameplan Admin"]:
			user_doc.remove(_role)
	user_doc.append_roles(role)
	user_doc.save(ignore_permissions=True)

	return get_user_info(user)[0]


@frappe.whitelist()
@validate_type
def remove_user(user: str):
	user_doc = frappe.get_doc("User", user)
	user_doc.enabled = 0
	user_doc.save(ignore_permissions=True)
	return user


@frappe.whitelist()
@validate_type
def invite_by_email(emails: str, role: str, projects: list = None):
	if not emails:
		return
	email_string = validate_email_address(emails, throw=False)
	email_list = split_emails(email_string)
	if not email_list:
		return
	existing_members = frappe.db.get_all("User", filters={"email": ["in", email_list]}, pluck="email")
	existing_invites = frappe.db.get_all(
		"GP Invitation",
		filters={
			"email": ["in", email_list],
			"role": ["in", ["Gameplan Admin", "Gameplan Member"]],
		},
		pluck="email",
	)

	if role == "Gameplan Guest":
		to_invite = list(set(email_list) - set(existing_invites))
	else:
		to_invite = list(set(email_list) - set(existing_members) - set(existing_invites))

	if projects:
		projects = frappe.as_json(projects, indent=None)

	for email in to_invite:
		frappe.get_doc(doctype="GP Invitation", email=email, role=role, projects=projects).insert(
			ignore_permissions=True
		)


@frappe.whitelist()
def unread_notifications():
	res = frappe.db.get_all(
		"GP Notification",
		"count(name) as count",
		{"to_user": frappe.session.user, "read": 0},
	)
	return res[0].count


@frappe.whitelist(allow_guest=True)
@validate_type
def accept_invitation(key: str = None):
	if not key:
		frappe.throw("Invalid or expired key")

	result = frappe.db.get_all("GP Invitation", filters={"key": key}, pluck="name")
	if not result:
		frappe.throw("Invalid or expired key")

	invitation = frappe.get_doc("GP Invitation", result[0])

	invitation.accept()
	invitation.reload()

	user = frappe.get_doc("User", invitation.email)
	needs_password_setup = user and not user.last_password_reset_date

	if invitation.status == "Accepted":
		if needs_password_setup:
			url = invitation.get_password_link()
			frappe.local.response["type"] = "redirect"
			frappe.local.response["location"] = f"{url}"
		else:
			frappe.local.login_manager.login_as(invitation.email)
			frappe.local.response["type"] = "redirect"
			frappe.local.response["location"] = "/g"


@frappe.whitelist()
def get_unsplash_photos(keyword=None):
	from gameplan.unsplash import get_by_keyword, get_list

	if keyword:
		return get_by_keyword(keyword)

	return frappe.cache().get_value("unsplash_photos", generator=get_list)


@frappe.whitelist()
def get_unread_items():
	Discussion = frappe.qb.DocType("GP Discussion")
	Visit = frappe.qb.DocType("GP Discussion Visit")
	query = (
		frappe.qb.from_(Discussion)
		.select(Discussion.team, Count(Discussion.team).as_("count"))
		.left_join(Visit)
		.on((Visit.discussion == Discussion.name) & (Visit.user == frappe.session.user))
		.where((Visit.last_visit.isnull()) | (Visit.last_visit < Discussion.last_post_at))
		.groupby(Discussion.team)
	)

	is_guest = gameplan.is_guest()
	if is_guest:
		GuestAccess = frappe.qb.DocType("GP Guest Access")
		project_list = GuestAccess.select(GuestAccess.project).where(GuestAccess.user == frappe.session.user)
		query = query.where(Discussion.project.isin(project_list))

	# pypika doesn't have any API for "FORCE INDEX FOR JOIN"
	sql = query.get_sql()
	sql = sql.replace(
		"LEFT JOIN `tabGP Discussion Visit`",
		"LEFT JOIN `tabGP Discussion Visit` FORCE INDEX FOR JOIN(discussion_user_index)",
	)
	data = frappe.db.sql(sql, as_dict=1)

	out = {}
	for d in data:
		out[d.team] = d.count
	return out


@frappe.whitelist()
def get_unread_items_by_project(projects):
	from frappe.query_builder.functions import Count

	project_names = frappe.parse_json(projects)
	Discussion = frappe.qb.DocType("GP Discussion")
	Visit = frappe.qb.DocType("GP Discussion Visit")
	query = (
		frappe.qb.from_(Discussion)
		.select(Discussion.project, Count(Discussion.project).as_("count"))
		.left_join(Visit)
		.on((Visit.discussion == Discussion.name) & (Visit.user == frappe.session.user))
		.where((Visit.last_visit.isnull()) | (Visit.last_visit < Discussion.last_post_at))
		.where(Discussion.project.isin(project_names))
		.groupby(Discussion.project)
	)

	data = query.run(as_dict=1)
	out = {}
	for d in data:
		out[d.project] = d.count
	return out


@frappe.whitelist()
def mark_all_notifications_as_read():
	for d in frappe.db.get_all(
		"GP Notification",
		filters={"to_user": frappe.session.user, "read": 0},
		pluck="name",
	):
		doc = frappe.get_doc("GP Notification", d)
		doc.read = 1
		doc.save(ignore_permissions=True)


@frappe.whitelist()
def recent_projects():
	from frappe.query_builder.functions import Max

	ProjectVisit = frappe.qb.DocType("GP Project Visit")
	Team = frappe.qb.DocType("GP Team")
	Project = frappe.qb.DocType("GP Project")
	Pin = frappe.qb.DocType("GP Pinned Project")
	pinned_projects_query = frappe.qb.from_(Pin).select(Pin.project).where(Pin.user == frappe.session.user)
	projects = (
		frappe.qb.from_(ProjectVisit)
		.select(
			ProjectVisit.project.as_("name"),
			Project.team,
			Project.title.as_("project_title"),
			Team.title.as_("team_title"),
			Project.icon,
			Max(ProjectVisit.last_visit).as_("timestamp"),
		)
		.left_join(Project)
		.on(Project.name == ProjectVisit.project)
		.left_join(Team)
		.on(Team.name == Project.team)
		.groupby(ProjectVisit.project)
		.where(ProjectVisit.user == frappe.session.user)
		.where(ProjectVisit.project.notin(pinned_projects_query))
		.orderby(ProjectVisit.last_visit, order=frappe.qb.desc)
		.limit(12)
	)

	return projects.run(as_dict=1)


@frappe.whitelist()
def active_projects():
	from frappe.query_builder.functions import Count

	Comment = frappe.qb.DocType("GP Comment")
	Discussion = frappe.qb.DocType("GP Discussion")
	CommentCount = Count(Comment.name).as_("comments_count")
	active_projects = (
		frappe.qb.from_(Comment)
		.select(CommentCount, Discussion.project)
		.left_join(Discussion)
		.on(Discussion.name == Comment.reference_name)
		.where(Comment.reference_doctype == "GP Discussion")
		.where(Comment.creation > frappe.utils.add_days(frappe.utils.now(), -70))
		.groupby(Discussion.project)
		.orderby(CommentCount, order=frappe.qb.desc)
		.limit(12)
	).run(as_dict=1)

	projects = frappe.qb.get_query(
		"GP Project",
		fields=[
			"name",
			"title as project_title",
			"team",
			"team.title as team_title",
			"icon",
			"modified as timestamp",
		],
		filters={"name": ("in", [d.project for d in active_projects])},
	).run(as_dict=1)

	active_projects_comment_count = {d.project: d.comments_count for d in active_projects}
	for d in projects:
		d.comments_count = active_projects_comment_count.get(str(d.name), 0)

	projects.sort(key=lambda d: d.comments_count, reverse=True)

	return projects


@frappe.whitelist()
def onboarding(space, icon, emails):
	emails = frappe.parse_json(emails)
	project = frappe.get_doc(doctype="GP Project", title=space, icon=icon).insert()
	invite_by_email(", ".join(emails), role="Gameplan Member")
	return project.name


@frappe.whitelist(allow_guest=True)
def oauth_providers():
	from frappe.utils.html_utils import get_icon_html
	from frappe.utils.oauth import get_oauth2_authorize_url, get_oauth_keys
	from frappe.utils.password import get_decrypted_password

	out = []
	providers = frappe.get_all(
		"Social Login Key",
		filters={"enable_social_login": 1},
		fields=["name", "client_id", "base_url", "provider_name", "icon"],
		order_by="name",
	)

	for provider in providers:
		client_secret = get_decrypted_password("Social Login Key", provider.name, "client_secret")
		if not client_secret:
			continue

		icon = None
		if provider.icon:
			if provider.provider_name == "Custom":
				icon = get_icon_html(provider.icon, small=True)
			else:
				icon = f"<img src='{provider.icon}' alt={provider.provider_name}>"

		if provider.client_id and provider.base_url and get_oauth_keys(provider.name):
			out.append(
				{
					"name": provider.name,
					"provider_name": provider.provider_name,
					"auth_url": get_oauth2_authorize_url(provider.name, "/g"),
					"icon": icon,
				}
			)
	return out


@frappe.whitelist()
def search(query, start=0):
	from gameplan.search import GameplanSearch

	search = GameplanSearch()
	query = search.clean_query(query)

	query_parts = query.split(" ")
	if len(query_parts) == 1 and not query_parts[0].endswith("*"):
		query = f"{query_parts[0]}*"
	if len(query_parts) > 1:
		query = " ".join([f"%%{q}%%" for q in query_parts])

	result = search.search(
		f"@title|content:({query})",
		start=start,
		sort_by="modified desc",
		highlight=True,
		with_payloads=True,
	)

	comments_by_doctype = {}
	grouped_results = {}
	for d in result.docs:
		doctype, name = d.id.split(":")
		d.doctype = doctype
		d.name = name
		del d.id
		if doctype == "GP Comment":
			comments_by_doctype.setdefault(d.payload["reference_doctype"], []).append(d)
		else:
			d.project = d.payload.get("project")
			d.team = d.payload.get("team")
			del d.payload
			grouped_results.setdefault(doctype, []).append(d)

	discussion_names = [d.payload["reference_name"] for d in comments_by_doctype.get("GP Discussion", [])]
	task_names = [d.payload["reference_name"] for d in comments_by_doctype.get("GP Task", [])]

	if discussion_names:
		for d in frappe.get_all(
			"GP Discussion",
			fields=["name", "title", "last_post_at", "project", "team"],
			filters={"name": ("in", discussion_names)},
		):
			d.doctype = "GP Discussion"
			d.name = cstr(d.name)
			d.content = ""
			d.via_comment = True
			d.modified = d.last_post_at
			for c in comments_by_doctype.get("GP Discussion", []):
				if c.payload["reference_name"] == d.name:
					d.content = c.content
			grouped_results.setdefault("GP Discussion", []).append(d)

	if task_names:
		for d in frappe.get_all(
			"GP Task",
			fields=["name", "title", "modified", "project", "team"],
			filters={"name": ("in", task_names)},
		):
			d.doctype = "GP Task"
			d.name = cstr(d.name)
			d.content = ""
			d.via_comment = True
			for c in comments_by_doctype.get("GP Task", []):
				if c.payload["reference_name"] == d.name:
					d.content = c.content
			grouped_results.setdefault("GP Task", []).append(d)

	return {
		"results": grouped_results,
		"total": result.total,
		"duration": result.duration,
	}


@frappe.whitelist()
def search2(query):
	from gameplan.search2 import GameplanSearch

	search = GameplanSearch()
	result = search.search(query)
	return result


@frappe.whitelist()
def search_sqlite(query, filters=None):
	from gameplan.search_sqlite import GameplanSearch

	search = GameplanSearch()

	# Parse filters if provided as JSON string
	if filters and isinstance(filters, str):
		import json

		filters = json.loads(filters)

	result = search.search(query, filters=filters)
	return result


# Artwork Management API Endpoints

@frappe.whitelist(allow_guest=False, methods=['POST', 'GET'])
def test_artwork_api():
	"""Test API endpoint to check if basic API access works"""
	frappe.log_error("Test API called successfully", "Artwork API Test")
	return {
		"success": True,
		"message": "API is working",
		"user": frappe.session.user,
		"user_roles": frappe.get_roles(frappe.session.user),
		"timestamp": frappe.utils.now()
	}

@frappe.whitelist(methods=['POST', 'GET'])
@validate_type
def get_customers():
	"""Get list of customers (GP Projects that represent customers)"""
	user_roles = frappe.get_roles(frappe.session.user)
	# Log only essential info to avoid character limit exceeded error
	frappe.log_error(f"get_customers called by user: {frappe.session.user}", "Artwork API Debug")
	
	artwork_roles = ["Sales Role", "Procurement Role", "Quality Role"]
	has_artwork_role = any(role in user_roles for role in artwork_roles)
	
	# Allow System Manager and Gameplan roles access
	if not has_artwork_role and "System Manager" not in user_roles and "Gameplan Admin" not in user_roles and "Gameplan Member" not in user_roles:
		frappe.throw("You don't have permission to view customers")
	
	customers = frappe.get_all(
		"GP Project",
		fields=["name", "title", "description", "modified"],
		order_by="title asc"
	)
	
	frappe.log_error(f"get_customers returning {len(customers)} customers", "Artwork API Debug")
	return customers

@frappe.whitelist()
def get_artworks():
	"""Get all artworks for filtering"""
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Only Procurement Role, Quality Role, and admins can access
	allowed_roles = ["Procurement Role", "Quality Role", "System Manager", "Gameplan Admin"]
	if not any(role in user_roles for role in allowed_roles):
		frappe.throw("You don't have permission to view artworks")
	
	artworks = frappe.get_all("GP Artwork",
		fields=["name", "title"],
		order_by="title"
	)
	
	return artworks


@frappe.whitelist(methods=['POST', 'GET'])
def get_customer_artworks(customer):
	"""Get artworks for a specific customer"""
	# Ensure customer is a string (handle both string and int inputs)
	customer = str(customer)
	user_roles = frappe.get_roles(frappe.session.user)
	# Log only essential info to avoid character limit exceeded error
	frappe.log_error(f"get_customer_artworks called for customer: {customer}, by user: {frappe.session.user}", "Artwork API Debug")
	
	artwork_roles = ["Sales Role", "Procurement Role", "Quality Role"]
	has_artwork_role = any(role in user_roles for role in artwork_roles)
	
	# Allow System Manager and Gameplan roles access
	if not has_artwork_role and "System Manager" not in user_roles and "Gameplan Admin" not in user_roles and "Gameplan Member" not in user_roles:
		frappe.throw("You don't have permission to view artworks")
	
	artworks = frappe.get_all(
		"GP Artwork",
		filters={"customer": customer},
		fields=[
			"name", "title", "description", "status", "priority", "project_type",
			"start_date", "due_date", "estimated_hours", "budget", 
			"created_by_sales", "modified"
		],
		order_by="modified desc"
	)
	
	# Add task count for each artwork (count both doctypes)
	for artwork in artworks:
		sales_task_count = frappe.db.count("GP Sales Task", {"artwork": artwork["name"]})
		procurement_task_count = frappe.db.count("GP Procurement Task", {"artwork": artwork["name"]})
		artwork["task_count"] = sales_task_count + procurement_task_count
	
	return artworks


@frappe.whitelist(methods=['POST', 'GET'])
def create_artwork(customer, title, description="", priority="Medium",
					 project_type="", start_date=None, due_date=None,
					 estimated_hours=0, budget=0):
	"""Create a new artwork for a customer"""
	# Convert parameters to proper types
	customer = str(customer)
	title = str(title)
	description = str(description) if description else ""
	priority = str(priority) if priority else "Medium"
	project_type = str(project_type) if project_type else ""
	estimated_hours = float(estimated_hours) if estimated_hours else 0
	budget = float(budget) if budget else 0
	
	user_roles = frappe.get_roles(frappe.session.user)
	# Log only essential info to avoid character limit exceeded error
	frappe.log_error(f"create_artwork called with customer: {customer}, title: {title}, by user: {frappe.session.user}", "Artwork API Debug")
	
	# Allow Sales Role to create artworks
	if "Sales Role" not in user_roles and "System Manager" not in user_roles and "Gameplan Admin" not in user_roles and "Gameplan Member" not in user_roles:
		frappe.throw("Only Sales Role can create artworks")
	
	artwork = frappe.new_doc("GP Artwork")
	artwork.customer = customer
	artwork.title = title
	artwork.description = description
	artwork.priority = priority
	if project_type:
		artwork.project_type = project_type
	if start_date:
		artwork.start_date = start_date
	if due_date:
		artwork.due_date = due_date
	if estimated_hours:
		artwork.estimated_hours = estimated_hours
	if budget:
		artwork.budget = budget
	
	artwork.insert()
	return artwork


@frappe.whitelist(methods=['POST', 'GET'])
def update_artwork(artwork_name, title=None, description=None, priority=None,
				  project_type=None, start_date=None, due_date=None,
				  estimated_hours=None, budget=None):
	"""Update an existing artwork"""
	# Convert parameters to proper types
	artwork_name = str(artwork_name)
	if title is not None:
		title = str(title)
	if description is not None:
		description = str(description)
	if priority is not None:
		priority = str(priority)
	if project_type is not None:
		project_type = str(project_type)
	if estimated_hours is not None:
		estimated_hours = float(estimated_hours)
	if budget is not None:
		budget = float(budget)
	
	user_roles = frappe.get_roles(frappe.session.user)
	if "Sales Role" not in user_roles and "System Manager" not in user_roles and "Gameplan Admin" not in user_roles:
		frappe.throw("Only Sales Role can update artworks")
	
	artwork = frappe.get_doc("GP Artwork", artwork_name)
	
	if title is not None:
		artwork.title = title
	if description is not None:
		artwork.description = description
	if priority is not None:
		artwork.priority = priority
	if project_type is not None:
		artwork.project_type = project_type
	if start_date is not None:
		artwork.start_date = start_date
	if due_date is not None:
		artwork.due_date = due_date
	if estimated_hours is not None:
		artwork.estimated_hours = estimated_hours
	if budget is not None:
		artwork.budget = budget
	
	artwork.save()
	return artwork


@frappe.whitelist()
def get_artwork_tasks(artwork=None, filters=None, fields=None, order_by="modified desc", limit=20):
	"""Get artwork tasks with filtering and permissions"""
	# Convert parameters to proper types
	if artwork is not None:
		artwork = str(artwork)
	if filters is None:
		filters = {}
	if fields is None:
		fields = [
			"name", "title", "status", "artwork", "customer", "assigned_to", 
			"priority", "created_by_sales", "modified", "owner", "cycle_count"
		]
	order_by = str(order_by) if order_by else "modified desc"
	limit = int(limit) if limit else 20
	
	if artwork:
		filters["artwork"] = artwork
	
	if not fields:
		fields = [
			"name", "title", "status", "artwork", "customer", "assigned_to", 
			"priority", "created_by_sales", "modified", "owner", "cycle_count"
		]
	
	# Add permission filters based on user role
	user_roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in user_roles and "Gameplan Admin" not in user_roles:
		artwork_roles = ["Sales Role", "Procurement Role", "Quality Role"]
		has_artwork_role = any(role in user_roles for role in artwork_roles)
		
		if not has_artwork_role:
			frappe.throw("You don't have permission to view artwork tasks")
	
	# Get tasks from both doctypes with appropriate fields
	sales_fields = [f for f in fields if f != "created_by_procurement"]
	if "created_by_sales" not in sales_fields:
		sales_fields.append("created_by_sales")
	
	procurement_fields = [f for f in fields if f != "created_by_sales"]
	if "created_by_procurement" not in procurement_fields:
		procurement_fields.append("created_by_procurement")
	
	sales_tasks = frappe.get_all(
		"GP Sales Task",
		filters=filters,
		fields=sales_fields,
		order_by=order_by,
		limit=limit
	)
	
	procurement_tasks = frappe.get_all(
		"GP Procurement Task",
		filters=filters,
		fields=procurement_fields,
		order_by=order_by,
		limit=limit
	)
	
	# Add workflow_type and cycle_count to each task, and normalize field names
	for task in sales_tasks:
		task["workflow_type"] = "Sales Cycle"
		# For sales tasks, cycle_count represents how many procurement tasks were created from this sales task
		if not task.get("cycle_count"):
			task["cycle_count"] = 0
		# Ensure created_by_sales is available for compatibility
		if "created_by_sales" not in task:
			task["created_by_sales"] = task.get("created_by_sales")
	for task in procurement_tasks:
		task["workflow_type"] = "Procurement Cycle"
		# For procurement tasks, cycle_count represents the cycle number for this specific procurement task
		if not task.get("cycle_count"):
			task["cycle_count"] = 1
		# Map created_by_procurement to created_by_sales for compatibility
		task["created_by_sales"] = task.get("created_by_procurement")
	
	# Combine and sort tasks
	all_tasks = sales_tasks + procurement_tasks
	all_tasks.sort(key=lambda x: x.get("modified", ""), reverse=True)
	
	# Add artwork and customer titles for display
	for task in all_tasks:
		if task.get("artwork"):
			task["artwork_title"] = frappe.db.get_value("GP Artwork", task["artwork"], "title")
		if task.get("customer"):
			task["customer_title"] = frappe.db.get_value("GP Project", task["customer"], "title")
	
	return all_tasks[:limit]


@frappe.whitelist()
def get_artwork_kanban_data():
	"""Get artwork tasks organized by status for Kanban view with role-based filtering"""
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Define statuses for both workflows
	sales_statuses = ["Draft", "Quality Review", "Rework", "Completed"]
	procurement_statuses = ["Procurement Draft", "Procurement Review", "Procurement Rework", "Final Approved"]
	bucket_statuses = ["Bucket"]  # For both Sales and Procurement buckets
	
	# Show all statuses for all users - let frontend handle workflow type filtering
	statuses = list(set(sales_statuses + procurement_statuses + bucket_statuses))
	
	result = {}
	for status in statuses:
		filters = {"status": status}
		
		# Don't filter by workflow type here - let frontend handle it
		# This allows users to see both sales and procurement tasks and filter on frontend
		
		tasks = get_artwork_tasks(filters=filters, limit=100)
		
		# Debug: Log tasks for each status
		if status == "Draft":
			frappe.log_error(f"Found {len(tasks)} tasks in Draft status: {[t.get('name') for t in tasks]}")
		
		# Add status history for each task
		for task in tasks:
			status_history = frappe.get_all(
				"GP Artwork Status History",
				filters={"parent": task["name"]},
				fields=["from_status", "to_status", "changed_by", "change_date"],
				order_by="change_date asc"
			)
			task["status_history"] = status_history
			# Add workflow_type based on doctype
			if "workflow_type" not in task:
				# Determine workflow type based on which doctype the task came from
				if task.get("doctype") == "GP Sales Task":
					task["workflow_type"] = "Sales Cycle"
				elif task.get("doctype") == "GP Procurement Task":
					task["workflow_type"] = "Procurement Cycle"
				else:
					# Fallback: check which doctype contains this task
					if frappe.db.exists("GP Sales Task", task["name"]):
						task["workflow_type"] = "Sales Cycle"
					elif frappe.db.exists("GP Procurement Task", task["name"]):
						task["workflow_type"] = "Procurement Cycle"
		
		result[status] = tasks
	
	# Special handling for Sales Cycle: include Completed status tasks in Bucket status
	# This allows the frontend to show completed sales tasks in the Sales Bucket column
	if "Bucket" in result:
		# Get completed sales tasks and add them to the Bucket status
		completed_sales_tasks = get_artwork_tasks(filters={"status": "Completed"}, limit=100)
		completed_sales_tasks = [task for task in completed_sales_tasks if task.get("workflow_type") == "Sales Cycle"]
		
		# Add status history for completed sales tasks
		for task in completed_sales_tasks:
			status_history = frappe.get_all(
				"GP Artwork Status History",
				filters={"parent": task["name"]},
				fields=["from_status", "to_status", "changed_by", "change_date"],
				order_by="change_date asc"
			)
			task["status_history"] = status_history
		
		# Add completed sales tasks to the Bucket status
		result["Bucket"].extend(completed_sales_tasks)
	
	return result


@frappe.whitelist(methods=['POST', 'GET'])
def create_artwork_task(title, artwork, description="", priority="Medium", assigned_to=None, workflow_type=None):
	"""Create a new artwork task with specified workflow type"""
	# Convert parameters to proper types
	title = str(title)
	artwork = str(artwork)
	description = str(description) if description else ""
	priority = str(priority) if priority else "Medium"
	if assigned_to is not None:
		assigned_to = str(assigned_to)
	
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Determine workflow type based on user role if not specified
	if not workflow_type:
		if "Sales Role" in user_roles:
			workflow_type = "Sales Cycle"
		elif "Procurement Role" in user_roles:
			workflow_type = "Procurement Cycle"
		else:
			workflow_type = "Sales Cycle"  # Default
	
	# Role-based creation permission
	if "Sales Role" not in user_roles and "Procurement Role" not in user_roles and "System Manager" not in user_roles and "Gameplan Admin" not in user_roles:
		frappe.throw("Only Sales Role or Procurement Role can create artwork tasks")
	
	# Verify artwork exists and get customer
	artwork_doc = frappe.get_doc("GP Artwork", artwork)
	
	# Create task in appropriate doctype based on workflow type
	if workflow_type == "Sales Cycle":
		task = frappe.new_doc("GP Sales Task")
	else:  # Procurement Cycle
		task = frappe.new_doc("GP Procurement Task")
	
	task.title = title
	task.artwork = artwork
	task.customer = artwork_doc.customer
	task.description = description
	task.priority = priority
	if assigned_to:
		task.assigned_to = assigned_to
	
	task.insert()
	return task


@frappe.whitelist(methods=['POST', 'GET'])
def create_sales_cycle_task(title, artwork, description="", priority="Medium", assigned_to=None):
	"""Create a new Sales Cycle artwork task"""
	return create_artwork_task(title, artwork, description, priority, assigned_to, "Sales Cycle")


@frappe.whitelist(methods=['POST', 'GET'])
def create_procurement_cycle_task(title, artwork, description="", priority="Medium", assigned_to=None):
	"""Create a new Procurement Cycle artwork task"""
	return create_artwork_task(title, artwork, description, priority, assigned_to, "Procurement Cycle")


@frappe.whitelist()
def get_artwork_task_transitions(task_name):
	"""Get available status transitions for an artwork task"""
	task_name = str(task_name)
	
	# Try to find the task in either doctype
	task = None
	try:
		task = frappe.get_doc("GP Sales Task", task_name)
	except frappe.DoesNotExistError:
		try:
			task = frappe.get_doc("GP Procurement Task", task_name)
		except frappe.DoesNotExistError:
			frappe.throw(f"Task {task_name} not found in either GP Sales Task or GP Procurement Task")
	
	return task.get_status_transitions()


@frappe.whitelist()
def update_artwork_task_status(task_name, new_status, reason="", comments=""):
	"""Update artwork task status with validation"""
	# Convert parameters to proper types
	task_name = str(task_name)
	new_status = str(new_status)
	reason = str(reason) if reason else ""
	comments = str(comments) if comments else ""
	
	# Try to find the task in either doctype
	task = None
	try:
		task = frappe.get_doc("GP Sales Task", task_name)
	except frappe.DoesNotExistError:
		try:
			task = frappe.get_doc("GP Procurement Task", task_name)
		except frappe.DoesNotExistError:
			try:
				task = frappe.get_doc("GP Artwork Task", task_name)
			except frappe.DoesNotExistError:
				frappe.throw(f"Task {task_name} not found in GP Sales Task, GP Procurement Task, or GP Artwork Task")
	
	return task.change_status(new_status, reason, comments)


@frappe.whitelist()
def get_approved_artwork_tasks(search_term: str = ""):
	"""Get approved artwork tasks for the report view - only actual approved tasks, not completed sales tasks"""
	filters = {
		"status": ["in", ["Approved", "Final Approved"]]
	}
	
	if search_term:
		filters["title"] = ["like", f"%{search_term}%"]
	
	tasks = get_artwork_tasks(
		filters=filters,
		fields=[
			"name", "title", "status", "artwork", "customer",
			"modified", "owner", "creation"
		],
		limit=500
	)
	
	# Add artwork and customer titles, and workflow type info
	for task in tasks:
		if task.get("artwork"):
			task["artwork_title"] = frappe.db.get_value("GP Artwork", task["artwork"], "title")
		if task.get("customer"):
			task["customer_title"] = frappe.db.get_value("GP Project", task["customer"], "title")
	
	return tasks


@frappe.whitelist()
def get_related_tasks(task_name):
	"""Get related tasks (sales/procurement cycle connections)"""
	task_name = str(task_name)
	task = frappe.get_doc("GP Artwork Task", task_name)
	
	related_tasks = {
		"procurement_task": task.get_related_procurement_task(),
		"sales_task": task.get_related_sales_task()
	}
	
	return related_tasks


@frappe.whitelist()
def get_artwork_task_details(task_name):
	"""Get detailed artwork task information"""
	# Convert parameters to proper types
	task_name = str(task_name)
	
	# Try to find the task in either doctype
	task = None
	doctype = None
	
	try:
		task = frappe.get_doc("GP Sales Task", task_name)
		doctype = "GP Sales Task"
	except frappe.DoesNotExistError:
		try:
			task = frappe.get_doc("GP Procurement Task", task_name)
			doctype = "GP Procurement Task"
		except frappe.DoesNotExistError:
			frappe.throw(f"Task {task_name} not found in either GP Sales Task or GP Procurement Task")
	
	# Get related tasks - handle missing methods gracefully
	related_tasks = {
		"procurement_task": None,
		"sales_task": None
	}
	
	# Try to get related tasks if methods exist
	try:
		if hasattr(task, 'get_related_procurement_task'):
			related_tasks["procurement_task"] = task.get_related_procurement_task()
		if hasattr(task, 'get_related_sales_task'):
			related_tasks["sales_task"] = task.get_related_sales_task()
	except Exception as e:
		frappe.log_error(f"Error getting related tasks: {str(e)}")
		# Keep related_tasks as None values
	
	# Get comments with attachments
	comments = frappe.get_all(
		"GP Comment",
		filters={"reference_doctype": doctype, "reference_name": task_name},
		fields=["name", "content", "attachments", "owner", "creation", "modified"],
		order_by="creation asc"
	)
	
	# Parse JSON attachments for each comment
	for comment in comments:
		if comment.get('attachments'):
			try:
				import json
				comment['attachments'] = json.loads(comment['attachments'])
			except:
				comment['attachments'] = []
		else:
			comment['attachments'] = []
	
	# Get allowed status transitions
	allowed_transitions = task.get_status_transitions()
	frappe.log_error(f"Task {task_name} transitions: {allowed_transitions}, Status: {task.status}, Doctype: {doctype}")
	
	# Add workflow_type and cycle_count to task data
	task_dict = task.as_dict()
	task_dict["workflow_type"] = "Sales Cycle" if doctype == "GP Sales Task" else "Procurement Cycle"
	if not task_dict.get("cycle_count"):
		task_dict["cycle_count"] = 0 if doctype == "GP Sales Task" else 1
	
	return {
		"task": task_dict,
		"comments": comments,
		"allowed_transitions": allowed_transitions,
		"related_tasks": related_tasks
	}


@frappe.whitelist()
def add_artwork_task_attachment(task_name, file_url, file_name, version="1.0", description="", file_size=""):
	"""Add an attachment to an artwork task"""
	# Convert parameters to proper types
	task_name = str(task_name)
	file_url = str(file_url)
	file_name = str(file_name)
	version = str(version) if version else "1.0"
	description = str(description) if description else ""
	file_size = str(file_size) if file_size else ""
	
	# Get the task document - try both doctypes
	task = None
	doctype = None
	
	try:
		task = frappe.get_doc("GP Sales Task", task_name)
		doctype = "GP Sales Task"
	except frappe.DoesNotExistError:
		try:
			task = frappe.get_doc("GP Procurement Task", task_name)
			doctype = "GP Procurement Task"
		except frappe.DoesNotExistError:
			frappe.throw(f"Task {task_name} not found in either GP Sales Task or GP Procurement Task")
	
	# Add attachment as a child table row
	attachment_row = task.append("attachments", {})
	attachment_row.file_name = file_name
	attachment_row.file_url = file_url
	attachment_row.version = version
	attachment_row.description = description
	attachment_row.file_size = file_size
	attachment_row.uploaded_by = frappe.session.user
	attachment_row.upload_date = frappe.utils.now()
	
	# Save the parent document with the new attachment
	task.save()
	
	return attachment_row.as_dict()


@frappe.whitelist()
def add_artwork_task_comment(task_name, content, attachments=None):
	"""Add a comment to an artwork task with optional attachments"""
	# Convert parameters to proper types
	task_name = str(task_name)
	content = str(content).strip()
	
	# Handle attachments parameter
	if attachments and isinstance(attachments, str):
		try:
			import json
			attachments = json.loads(attachments)
		except:
			attachments = []
	elif not attachments:
		attachments = []
	
	# Check if we have content or attachments
	if not content and not attachments:
		frappe.throw("Comment must have either content or attachments")
	
	# Verify the task exists and user has access - try both doctypes
	task = None
	doctype = None
	try:
		task = frappe.get_doc("GP Sales Task", task_name)
		doctype = "GP Sales Task"
	except frappe.DoesNotExistError:
		try:
			task = frappe.get_doc("GP Procurement Task", task_name)
			doctype = "GP Procurement Task"
		except frappe.DoesNotExistError:
			frappe.throw(f"Task {task_name} not found in either GP Sales Task or GP Procurement Task")
	
	# Create the comment
	comment = frappe.new_doc("GP Comment")
	comment.reference_doctype = doctype
	comment.reference_name = task_name
	comment.content = content if content else "[File attachments]"
	
	# Set attachments as JSON string in Long Text field
	if attachments:
		import json
		comment.attachments = json.dumps(attachments)
	else:
		comment.attachments = None
		
	comment.owner = frappe.session.user
	
	# Save the comment
	comment.insert()
	
	# Send real-time notification
	from gameplan.realtime_artwork import notify_artwork_task_update
	notify_artwork_task_update(task_name, "comment_added", {
		"comment_id": comment.name,
		"content": content,
		"attachments": attachments,
		"user": frappe.session.user
	})
	
	return comment.as_dict()


@frappe.whitelist()
def get_search_filter_options():
	"""Get available filter options for advanced search"""
	from gameplan.search_sqlite import GameplanSearch

	search = GameplanSearch()
	return search.get_filter_options()


@frappe.whitelist()
def get_bucket_tasks(customer_filter=None, sort_by="cycle_count", sort_order="desc"):
	"""Get all Bucket tasks for Procurement team (Procurement Bucket)"""
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Only Procurement Role and admins can access bucket
	if "Procurement Role" not in user_roles and "System Manager" not in user_roles and "Gameplan Admin" not in user_roles:
		frappe.throw("You don't have permission to view bucket tasks")
	
	# Build filters - Bucket tasks are in the Procurement Bucket
	# Include both "Bucket" and "Final Approved" tasks as they are ready for procurement processing
	filters = {
		"status": ["in", ["Bucket", "Final Approved"]]
	}
	
	# Add customer filter if provided
	if customer_filter:
		filters["customer"] = customer_filter
	
	# Get tasks from both doctypes that are Final Approved
	sales_tasks = frappe.get_all("GP Sales Task",
		filters=filters,
		fields=[
			"name", "title", "artwork", "customer", "priority", 
			"modified", "created_by_sales",
			"last_status_change", "last_status_changed_by",
			"cycle_count"
		],
		order_by=f"{sort_by} {sort_order}"
	)
	
	procurement_tasks = frappe.get_all("GP Procurement Task",
		filters=filters,
		fields=[
			"name", "title", "artwork", "customer", "priority", 
			"modified", "created_by_procurement",
			"last_status_change", "last_status_changed_by",
			"sales_task_reference", "cycle_count"
		],
		order_by=f"{sort_by} {sort_order}"
	)
	
	# Combine tasks and add workflow_type
	all_tasks = []
	
	# Add sales tasks
	for task in sales_tasks:
		task.workflow_type = "Sales Cycle"
		task.created_by_procurement = None
		task.sales_task_reference = None
		all_tasks.append(task)
	
	# Add procurement tasks
	for task in procurement_tasks:
		task.workflow_type = "Procurement Cycle"
		task.created_by_sales = None
		all_tasks.append(task)
	
	# Add customer title and artwork title for all tasks
	for task in all_tasks:
		if task.customer:
			task.customer_title = frappe.db.get_value("GP Project", task.customer, "title")
		if task.artwork:
			task.artwork_title = frappe.db.get_value("GP Artwork", task.artwork, "title")
		
		# Add creator name
		if task.created_by_sales:
			task.created_by_sales_name = frappe.db.get_value("User", task.created_by_sales, "full_name")
		if task.created_by_procurement:
			task.created_by_procurement_name = frappe.db.get_value("User", task.created_by_procurement, "full_name")
		
		# Add source information
		task.source = "Completed Sales" if getattr(task, 'sales_task_reference', None) else "Direct Procurement"
	
	# Sort all tasks by the specified criteria
	all_tasks.sort(key=lambda x: x[sort_by] if sort_by in x else 0, reverse=(sort_order == 'desc'))
	
	return all_tasks

@frappe.whitelist()
def get_completed_sales_tasks(customer_filter=None, artwork_title_filter=None, artwork_filter=None, start_date=None, end_date=None, sort_by="modified", sort_order="desc", limit_start=0, limit_page_length=20):
	"""Get all completed Sales tasks that are ready for Procurement with pagination and filtering"""
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Only Procurement Role, Quality Role, and admins can access completed sales
	allowed_roles = ["Procurement Role", "Quality Role", "System Manager", "Gameplan Admin"]
	if not any(role in user_roles for role in allowed_roles):
		frappe.throw("You don't have permission to view completed sales tasks")
	
	# Build filters for completed sales tasks (both Completed and Bucket status for backward compatibility)
	filters = {
		"status": ["in", ["Completed", "Bucket"]]
	}
	
	# Add customer filter if provided
	if customer_filter:
		filters["customer"] = customer_filter
	
	# Add artwork filter if provided
	if artwork_filter:
		filters["artwork"] = artwork_filter
	
	# Add date filters if provided
	if start_date and end_date:
		filters["modified"] = ["between", [start_date, end_date]]
	elif start_date:
		filters["modified"] = [">=", start_date]
	elif end_date:
		filters["modified"] = ["<=", end_date]
	
	# Get completed sales tasks with pagination
	tasks = frappe.get_all("GP Sales Task",
		filters=filters,
		fields=[
			"name", "title", "artwork", "customer", "priority", 
			"modified", "created_by_sales",
			"last_status_change", "last_status_changed_by", "cycle_count"
		],
		order_by=f"{sort_by} {sort_order}",
		limit_start=limit_start,
		limit_page_length=limit_page_length
	)
	
	# Add customer title and artwork title
	for task in tasks:
		if task.customer:
			task.customer_title = frappe.db.get_value("GP Project", task.customer, "title") or "Unknown Customer"
		else:
			task.customer_title = "No Customer"
			
		if task.artwork:
			task.artwork_title = frappe.db.get_value("GP Artwork", task.artwork, "title") or "Unknown Artwork"
		else:
			task.artwork_title = "No Artwork"
			
		if task.created_by_sales:
			task.created_by_sales_name = frappe.db.get_value("User", task.created_by_sales, "full_name")
		
		# Add source information
		task.source = "Completed Sales"
		task.ready_for_procurement = True
		task.status = "Completed"  # Display status (actual status is "Bucket")
		task.actual_status = "Bucket"  # Keep track of actual status
		task.workflow_type = "Sales Cycle"  # Add workflow_type for compatibility
		
		# Ensure priority has a default value
		if not task.priority:
			task.priority = "Medium"
		
		# Check if procurement tasks exist for this sales task
		procurement_count = frappe.db.count("GP Procurement Task", {
			"sales_task_reference": task.name
		})
		
		task.in_procurement = procurement_count > 0
		task.cycle_count = procurement_count  # Keep for compatibility
		
		# Get the latest procurement task ID if exists
		if procurement_count > 0:
			latest_procurement = frappe.get_all("GP Procurement Task", 
				filters={
					"sales_task_reference": task.name
				},
				fields=["name"],
				order_by="modified desc",
				limit=1
			)
			if latest_procurement:
				task.procurement_task_id = latest_procurement[0].name
				task.cycle_number = procurement_count  # Use count as cycle number
	
	# Apply artwork title filter if provided (filter by task title, not artwork title)
	if artwork_title_filter:
		frappe.log_error(f"Filtering by task title: '{artwork_title_filter}'", "Artwork Filter Debug")
		original_count = len(tasks)
		tasks = [task for task in tasks if task.title and artwork_title_filter.lower() in task.title.lower()]
		frappe.log_error(f"Filtered from {original_count} to {len(tasks)} tasks", "Artwork Filter Debug")
	
	# Return the expected format for the frontend
	return {
		"tasks": tasks,
		"total_count": len(tasks),
		"has_more": False
	}

@frappe.whitelist()
def move_completed_sales_to_bucket(task_name):
	"""Move a completed sales task to the procurement bucket"""
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Only Procurement Role, Quality Role, and admins can move tasks to bucket
	allowed_roles = ["Procurement Role", "Quality Role", "System Manager", "Gameplan Admin"]
	if not any(role in user_roles for role in allowed_roles):
		frappe.throw("You don't have permission to move tasks to procurement bucket")
	
	try:
		# Get the task
		task = frappe.get_doc("GP Sales Task", task_name)
		
		# Verify it's a completed sales task (either Completed or Bucket status)
		if task.status not in ["Completed", "Bucket"]:
			frappe.throw("Only completed sales tasks can be moved to procurement bucket")
		
		# Create a new procurement task in bucket status
		procurement_task = frappe.new_doc("GP Procurement Task")
		procurement_task.title = f"{task.title} - Procurement"
		procurement_task.artwork = task.artwork
		procurement_task.customer = task.customer
		procurement_task.description = task.description
		procurement_task.priority = task.priority
		procurement_task.status = "Bucket"
		procurement_task.sales_task_reference = task.name
		procurement_task.created_by_procurement = frappe.session.user
		procurement_task.cycle_count = 1
		
		# Copy attachments if any
		if hasattr(task, 'attachments') and task.attachments:
			for attachment in task.attachments:
				procurement_task.append("attachments", {
					"file_name": attachment.file_name,
					"file_url": attachment.file_url,
					"version": attachment.version,
					"description": f"From Sales Task: {attachment.description}",
					"uploaded_by": frappe.session.user,
					"upload_date": now()
				})
		
		procurement_task.insert()
		
		# Send notification to procurement team
		frappe.publish_realtime("notify_artwork_task_update", {
			"task_name": procurement_task.name,
			"action": "moved_to_bucket",
			"message": f"Task '{task.title}' moved to procurement bucket"
		})
		
		return {"success": True, "message": "Task moved to procurement bucket successfully", "procurement_task_id": procurement_task.name}
		
	except Exception as e:
		frappe.log_error(f"Error moving task to bucket: {str(e)}")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def move_procurement_task_to_bucket(task_name):
	"""Move a Final Approved procurement task to bucket status"""
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Only Procurement Role, Quality Role, and admins can move tasks to bucket
	allowed_roles = ["Procurement Role", "Quality Role", "System Manager", "Gameplan Admin"]
	if not any(role in user_roles for role in allowed_roles):
		frappe.throw("You don't have permission to move tasks to procurement bucket")
	
	try:
		# Try to find the task in either doctype
		task = None
		doctype = None
		
		try:
			task = frappe.get_doc("GP Sales Task", task_name)
			doctype = "GP Sales Task"
		except frappe.DoesNotExistError:
			try:
				task = frappe.get_doc("GP Procurement Task", task_name)
				doctype = "GP Procurement Task"
			except frappe.DoesNotExistError:
				try:
					task = frappe.get_doc("GP Artwork Task", task_name)
					doctype = "GP Artwork Task"
				except frappe.DoesNotExistError:
					frappe.throw(f"Task {task_name} not found in any artwork task doctype")
		
		# Verify it's a Final Approved procurement task
		if task.status != "Final Approved":
			frappe.throw("Only Final Approved tasks can be moved to bucket")
		
		# Check workflow type based on doctype
		workflow_type = "Sales Cycle" if doctype == "GP Sales Task" else "Procurement Cycle"
		if workflow_type != "Procurement Cycle":
			frappe.throw("Only Procurement Cycle tasks can be moved to bucket")
		
		# Change status to Bucket
		task.status = "Bucket"
		task.save()
		
		# Send notification
		frappe.publish_realtime("notify_artwork_task_update", {
			"task_name": task.name,
			"action": "moved_to_bucket",
			"message": f"Task '{task.title}' moved to procurement bucket"
		})
		
		return {"success": True, "message": f"Task '{task.title}' moved to procurement bucket successfully"}
		
	except Exception as e:
		frappe.log_error(f"Error moving procurement task to bucket: {str(e)}")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def create_procurement_task_from_sales(sales_task_name):
	"""Create a new procurement task from a completed sales task"""
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Only Procurement Role, Quality Role, and admins can create procurement tasks
	allowed_roles = ["Procurement Role", "Quality Role", "System Manager", "Gameplan Admin"]
	if not any(role in user_roles for role in allowed_roles):
		frappe.throw("You don't have permission to create procurement tasks")
	
	try:
		# Get the sales task
		sales_task = frappe.get_doc("GP Sales Task", sales_task_name)
		
		# Verify it's a completed sales task
		if sales_task.status != "Completed":
			frappe.throw("Only completed sales tasks can be used to create procurement tasks")
		
		# Count existing procurement tasks for this sales task to determine cycle number
		existing_procurement_count = frappe.db.count("GP Procurement Task", {
			"sales_task_reference": sales_task_name
		})
		
		cycle_number = existing_procurement_count + 1
		
		# Create new procurement task
		procurement_task = frappe.new_doc("GP Procurement Task")
		procurement_task.title = f"{sales_task.title} - Procurement Cycle #{cycle_number}"
		procurement_task.artwork = sales_task.artwork
		procurement_task.customer = sales_task.customer
		procurement_task.description = sales_task.description
		procurement_task.priority = sales_task.priority
		procurement_task.status = "Procurement Draft"
		procurement_task.sales_task_reference = sales_task_name
		procurement_task.created_by_procurement = frappe.session.user
		procurement_task.cycle_count = cycle_number
		
		# Copy attachments if any
		if hasattr(sales_task, 'attachments') and sales_task.attachments:
			for attachment in sales_task.attachments:
				procurement_task.append("attachments", {
					"file_name": attachment.file_name,
					"file_url": attachment.file_url,
					"version": attachment.version,
					"description": f"From Sales Task: {attachment.description}",
					"uploaded_by": frappe.session.user,
					"upload_date": now()
				})
		
		procurement_task.insert(ignore_permissions=True)
		
		# Debug: Log the created task details
		frappe.log_error(f"Created procurement task: {procurement_task.name}, Status: {procurement_task.status}, Workflow: Procurement Cycle")
		
		# Send notification
		frappe.publish_realtime("notify_artwork_task_update", {
			"task_name": procurement_task.name,
			"action": "procurement_task_created",
			"message": f"Procurement task '{procurement_task.title}' created from sales task"
		})
		
		return {"success": True, "procurement_task_id": procurement_task.name, "cycle_number": cycle_number, "message": f"Procurement task created successfully (Cycle #{cycle_number})"}
		
	except Exception as e:
		frappe.log_error(f"Error creating procurement task: {str(e)}")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def move_task_from_bucket(task_name, new_status="Procurement Review"):
	"""Move a Bucket task from Procurement Bucket to active procurement workflow"""
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Only Procurement Role and admins can move tasks from bucket
	if "Procurement Role" not in user_roles and "System Manager" not in user_roles and "Gameplan Admin" not in user_roles:
		frappe.throw("You don't have permission to move tasks from bucket")
	
	try:
		# Try to find the task in either doctype
		task = None
		doctype = None
		
		try:
			task = frappe.get_doc("GP Sales Task", task_name)
			doctype = "GP Sales Task"
		except frappe.DoesNotExistError:
			try:
				task = frappe.get_doc("GP Procurement Task", task_name)
				doctype = "GP Procurement Task"
			except frappe.DoesNotExistError:
				frappe.throw(f"Task {task_name} not found in any artwork task doctype")
		
		# Verify it's a Bucket task
		if task.status != "Bucket":
			frappe.throw("Only Bucket tasks can be moved from Procurement Bucket")
		
		# Change status to the new status
		old_status = task.status
		task.status = new_status
		task.save()
		
		# Return a clean response
		return {
			"success": True,
			"message": f"Task '{task.title}' moved from Procurement Bucket to {new_status}",
			"task_name": task.name,
			"new_status": new_status
		}
	except Exception as e:
		frappe.log_error(f"Error moving task {task_name} from bucket: {str(e)}")
		frappe.throw(f"Failed to move task from bucket: {str(e)}")

@frappe.whitelist()
def get_bucket_stats():
	"""Get statistics for bucket tasks (Bucket status tasks)"""
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Only Procurement Role and admins can access bucket stats
	if "Procurement Role" not in user_roles and "System Manager" not in user_roles and "Gameplan Admin" not in user_roles:
		frappe.throw("You don't have permission to view bucket stats")
	
	# Get total Bucket tasks from both doctypes
	# Include both "Bucket" and "Final Approved" tasks as they are ready for procurement processing
	total_sales_tasks = frappe.db.count("GP Sales Task", {
		"status": ["in", ["Bucket", "Final Approved"]]
	})
	
	total_procurement_tasks = frappe.db.count("GP Procurement Task", {
		"status": ["in", ["Bucket", "Final Approved"]]
	})
	
	total_bucket_tasks = total_sales_tasks + total_procurement_tasks
	
	# Get tasks by customer from both doctypes
	customer_stats = frappe.db.sql("""
		SELECT t.customer, p.title as customer_title, COUNT(*) as count
		FROM (
			SELECT customer FROM `tabGP Sales Task` WHERE status IN ('Bucket', 'Final Approved')
			UNION ALL
			SELECT customer FROM `tabGP Procurement Task` WHERE status IN ('Bucket', 'Final Approved')
		) t
		LEFT JOIN `tabGP Project` p ON t.customer = p.name
		GROUP BY t.customer, p.title
		ORDER BY count DESC
	""", as_dict=True)
	
	return {
		"total_tasks": total_bucket_tasks,
		"customer_stats": customer_stats
	}

@frappe.whitelist()
def test_api():
	"""Simple test endpoint to verify API connectivity"""
	return {"status": "success", "message": "API is working", "user": frappe.session.user}


@frappe.whitelist()
def get_workflow_tasks(workflow_type=None, status=None, customer=None, limit=50):
	"""Get tasks filtered by workflow type and status with role-based access"""
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Build filters based on user role and parameters
	filters = {}
	
	# Role-based filtering
	if "System Manager" not in user_roles and "Gameplan Admin" not in user_roles:
		artwork_roles = ["Sales Role", "Procurement Role", "Quality Role"]
		has_artwork_role = any(role in user_roles for role in artwork_roles)
		
		if not has_artwork_role:
			frappe.throw("You don't have permission to view artwork tasks")
		
		# Sales Role: Only see Sales Cycle tasks
		if "Sales Role" in user_roles and "Quality Role" not in user_roles:
			filters["workflow_type"] = "Sales Cycle"
		
		# Procurement Role: Only see Procurement Cycle tasks (including Bucket)
		if "Procurement Role" in user_roles and "Quality Role" not in user_roles:
			filters["workflow_type"] = "Procurement Cycle"
		
		# Quality Role: Can see both workflows (no additional filter)
	
	# Add parameter filters
	if workflow_type:
		filters["workflow_type"] = workflow_type
	if status:
		filters["status"] = status
	if customer:
		filters["customer"] = customer
	
	# Get tasks from both doctypes with appropriate fields
	sales_tasks = frappe.get_all(
		"GP Sales Task",
		filters=filters,
		fields=[
			"name", "title", "status", "artwork", "customer", "assigned_to", 
			"priority", "created_by_sales", "modified", "owner", 
			"last_status_change", "last_status_changed_by", "cycle_count"
		],
		order_by="modified desc",
		limit=limit
	)
	
	procurement_tasks = frappe.get_all(
		"GP Procurement Task",
		filters=filters,
		fields=[
			"name", "title", "status", "artwork", "customer", "assigned_to", 
			"priority", "created_by_procurement", "modified", "owner", 
			"last_status_change", "last_status_changed_by", "cycle_count"
		],
		order_by="modified desc",
		limit=limit
	)
	
	# Add workflow_type to each task and normalize field names
	for task in sales_tasks:
		task["workflow_type"] = "Sales Cycle"
		# Ensure created_by_sales is available for compatibility
		if "created_by_sales" not in task:
			task["created_by_sales"] = task.get("created_by_sales")
	for task in procurement_tasks:
		task["workflow_type"] = "Procurement Cycle"
		# Map created_by_procurement to created_by_sales for compatibility
		task["created_by_sales"] = task.get("created_by_procurement")
	
	# Combine tasks
	tasks = sales_tasks + procurement_tasks
	tasks.sort(key=lambda x: x.get("modified", ""), reverse=True)
	
	# Add display information
	for task in tasks:
		if task.get("artwork"):
			task["artwork_title"] = frappe.db.get_value("GP Artwork", task["artwork"], "title")
		if task.get("customer"):
			task["customer_title"] = frappe.db.get_value("GP Project", task["customer"], "title")
		if task.get("created_by_sales"):
			task["created_by_sales_name"] = frappe.db.get_value("User", task["created_by_sales"], "full_name")
	
	return tasks


@frappe.whitelist()
def get_sales_cycle_tasks(customer=None, status=None, limit=50):
	"""Get Sales Cycle tasks for Sales team"""
	return get_workflow_tasks(workflow_type="Sales Cycle", status=status, customer=customer, limit=limit)


@frappe.whitelist()
def get_procurement_cycle_tasks(customer=None, status=None, limit=50):
	"""Get Procurement Cycle tasks for Procurement team"""
	return get_workflow_tasks(workflow_type="Procurement Cycle", status=status, customer=customer, limit=limit)


@frappe.whitelist()
def get_quality_review_tasks(workflow_type=None, limit=50):
	"""Get tasks that need quality review"""
	filters = {"status": "Quality Review"}
	if workflow_type:
		filters["workflow_type"] = workflow_type
	
	return get_workflow_tasks(workflow_type=workflow_type, status="Quality Review", limit=limit)


@frappe.whitelist()
def get_workflow_summary():
	"""Get summary statistics for the workflow system"""
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Check permissions
	artwork_roles = ["Sales Role", "Procurement Role", "Quality Role"]
	has_artwork_role = any(role in user_roles for role in artwork_roles)
	
	if not has_artwork_role and "System Manager" not in user_roles and "Gameplan Admin" not in user_roles:
		frappe.throw("You don't have permission to view workflow summary")
	
	summary = {}
	
	# Sales Cycle summary
	if "Sales Role" in user_roles or "Quality Role" in user_roles or "System Manager" in user_roles or "Gameplan Admin" in user_roles:
		sales_tasks = frappe.db.count("GP Sales Task")
		sales_by_status = frappe.db.sql("""
			SELECT status, COUNT(*) as count
			FROM `tabGP Sales Task`
			GROUP BY status
		""", as_dict=True)
		
		summary["sales_cycle"] = {
			"total": sales_tasks,
			"by_status": {item.status: item.count for item in sales_by_status}
		}
	
	# Procurement Cycle summary
	if "Procurement Role" in user_roles or "Quality Role" in user_roles or "System Manager" in user_roles or "Gameplan Admin" in user_roles:
		procurement_tasks = frappe.db.count("GP Procurement Task")
		procurement_by_status = frappe.db.sql("""
			SELECT status, COUNT(*) as count
			FROM `tabGP Procurement Task`
			GROUP BY status
		""", as_dict=True)
		
		summary["procurement_cycle"] = {
			"total": procurement_tasks,
			"by_status": {item.status: item.count for item in procurement_by_status}
		}
	
	# Bucket summary (only for Procurement and Quality roles) - Bucket tasks
	if "Procurement Role" in user_roles or "Quality Role" in user_roles or "System Manager" in user_roles or "Gameplan Admin" in user_roles:
		sales_bucket = frappe.db.count("GP Sales Task", {
			"status": "Bucket"
		})
		procurement_bucket = frappe.db.count("GP Procurement Task", {
			"status": "Bucket"
		})
		bucket_tasks = sales_bucket + procurement_bucket
		
		summary["bucket"] = {
			"total": bucket_tasks
		}
	
	return summary


@frappe.whitelist()
def create_task_from_bucket(task_name, new_title=None, assigned_to=None):
	"""Create a new Procurement Cycle task from a Bucket task"""
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Only Procurement Role and admins can create tasks from bucket
	if "Procurement Role" not in user_roles and "System Manager" not in user_roles and "Gameplan Admin" not in user_roles:
		frappe.throw("You don't have permission to create tasks from bucket")
	
	# Get the bucket task
	bucket_task = frappe.get_doc("GP Procurement Task", task_name)
	
	if bucket_task.status != "Bucket":
		frappe.throw("Task is not in Bucket status")
	
	# Create new task
	new_task = frappe.new_doc("GP Procurement Task")
	new_task.title = new_title or f"{bucket_task.title} - Active"
	new_task.artwork = bucket_task.artwork
	new_task.customer = bucket_task.customer
	new_task.description = bucket_task.description
	new_task.priority = bucket_task.priority
	new_task.status = "Draft"
	new_task.sales_task_reference = bucket_task.sales_task_reference
	new_task.created_by_procurement = frappe.session.user
	new_task.cycle_count = bucket_task.cycle_count or 1
	
	if assigned_to:
		new_task.assigned_to = assigned_to
	
	new_task.insert()
	
	# Move the bucket task to a different status to avoid duplication
	bucket_task.status = "Completed"
	bucket_task.save()
	
	return new_task


@frappe.whitelist()
def get_workflow_status_options(workflow_type):
	"""Get available status options for a workflow type"""
	if workflow_type == "Sales Cycle":
		return ["Draft", "Quality Review", "Rework", "Completed"]
	elif workflow_type == "Procurement Cycle":
		return ["Bucket", "Draft", "Procurement Review", "Quality Review", "Rework", "Final Approved", "Completed"]
	else:
		return []


def can_access_gameplan():
	"""Check if the app should be shown in /apps"""
	from frappe.utils.modules import get_modules_from_all_apps_for_user

	if frappe.session.user == "Administrator":
		return True

	allowed_modules = [x["module_name"] for x in get_modules_from_all_apps_for_user()]
	if "Gameplan" not in allowed_modules:
		return False

	roles = set(frappe.get_roles())
	allowed_roles = set(["System Manager", "Gameplan Admin", "Gameplan Member", "Gameplan Guest"])
	if roles.intersection(allowed_roles):
		return True

	return False

@frappe.whitelist()
def move_sales_task_to_bucket(task_name):
	"""Move a Completed sales task to bucket status"""
	user_roles = frappe.get_roles(frappe.session.user)
	
	# Only Sales Role, Quality Role, and admins can move tasks to bucket
	allowed_roles = ["Sales Role", "Quality Role", "System Manager", "Gameplan Admin"]
	if not any(role in user_roles for role in allowed_roles):
		frappe.throw("You don't have permission to move tasks to sales bucket")
	
	try:
		# Get the task
		task = frappe.get_doc("GP Sales Task", task_name)
		
		# Verify it's a Completed sales task
		if task.status != "Completed":
			frappe.throw("Only Completed tasks can be moved to bucket")
		
		if task.workflow_type != "Sales Cycle":
			frappe.throw("Only Sales Cycle tasks can be moved to bucket")
		
		# Change status to Bucket
		task.status = "Bucket"
		task.save()
		
		# Send notification
		frappe.publish_realtime("notify_artwork_task_update", {
			"task_name": task.name,
			"action": "moved_to_sales_bucket",
			"message": f"Task '{task.title}' moved to sales bucket"
		})
		
		return {"success": True, "message": f"Task '{task.title}' moved to sales bucket successfully"}
		
	except Exception as e:
		frappe.log_error(f"Error moving sales task to bucket: {str(e)}")
		return {"success": False, "message": str(e)}
