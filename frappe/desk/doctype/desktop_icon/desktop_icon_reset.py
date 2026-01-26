# Copyright (c) 2026, Frappe Technologies and contributors
# License: MIT. See LICENSE

"""
Desktop Icon Reset Utilities

This module provides functionality to update and recreate desktop icons
using standard Frappe methods for safe and controlled restoration.
Never deletes any icons - only updates from JSON files and creates missing ones.
"""

import frappe
from frappe import _


@frappe.whitelist()
def reset_all_desktop_icons():
	"""
	Update desktop icons using standard Frappe methods.

	This function performs a controlled update by:
	1. Importing desktop_icon files from JSON (updates standard icons)
	2. Using auto_generate_icons_and_sidebar() to create missing icons from existing workspace in DB

	Standard icons are never deleted - they are updated from JSON files.
	This preserves all standard icons and ensures they match the source files.

	This is useful when app_title has changed in hooks or when desktop icon
	structure needs to be updated from source files.

	Returns:
		dict: Statistics about the reset operation:
			- total_icons: Total number of icons after update
			- total_standard: Number of standard icons
			- errors: List of errors (if any)

	Raises:
		frappe.PermissionError: If user doesn't have write permission for Desktop Icon
	"""
	# Check permissions
	if not frappe.has_permission("Desktop Icon", "write"):
		frappe.throw(_("You do not have permission to reset desktop icons"))

	errors = []

	# Step 1: Clear cache before sync
	frappe.cache.delete_key("desktop_icons")
	frappe.db.commit()

	# Step 2: Import only desktop_icon files (following sync_for logic for app-level folders)
	# Workspace are not needed - create_desktop_icons_from_workspace() reads them from DB
	# If workspace are missing, auto_generate will create icons from existing workspace in DB
	original_developer_mode = frappe.conf.get("developer_mode", False)
	frappe.conf.developer_mode = False

	try:
		import os
		from frappe.modules.import_file import import_file_by_path
		from frappe.modules.utils import get_app_level_directory_path

		# Import desktop_icon files from app-level folders (same logic as sync_for)
		for app_name in frappe.get_installed_apps():
			directory_path = get_app_level_directory_path("desktop_icon", app_name)
			if os.path.exists(directory_path):
				icon_files = [
					os.path.join(directory_path, filename)
					for filename in os.listdir(directory_path)
					if filename.endswith(".json")
				]
				for doc_path in icon_files:
					if os.path.exists(doc_path):
						imported = import_file_by_path(
							doc_path, force=True, ignore_version=True, reset_permissions=False
						)
						if imported:
							frappe.db.commit(chain=True)
	except Exception as e:
		error_msg = _("Error importing desktop_icon files: {0}").format(str(e))
		errors.append(error_msg)
		frappe.log_error(
			title=_("Error importing desktop_icon files"),
			message=_("Failed to import desktop icon files: {0}").format(str(e)),
		)
	finally:
		frappe.conf.developer_mode = original_developer_mode

	# Step 3: Update all fields from JSON files (app, logo_url, standard, etc.)
	# import_file_by_path may not update all fields, so we explicitly update them from JSON
	try:
		import os
		import json
		from frappe.modules.utils import get_app_level_directory_path

		# Collect all icon data from JSON files
		icon_data_map = {}  # {label: icon_data_dict}
		
		for app_name in frappe.get_installed_apps():
			directory_path = get_app_level_directory_path("desktop_icon", app_name)
			if os.path.exists(directory_path):
				icon_files = [
					os.path.join(directory_path, filename)
					for filename in os.listdir(directory_path)
					if filename.endswith(".json")
				]
				for doc_path in icon_files:
					if os.path.exists(doc_path):
						try:
							with open(doc_path, "r") as f:
								icon_data = json.load(f)
								if icon_data.get("doctype") == "Desktop Icon":
									label = icon_data.get("label")
									if label:
										icon_data_map[label] = icon_data
						except Exception as e:
							frappe.log_error(
								title=_("Error reading JSON file"),
								message=_("Failed to read {0}: {1}").format(doc_path, str(e)),
							)

		# Update icons with data from JSON files
		if icon_data_map:
			for label, json_data in icon_data_map.items():
				try:
					icon = frappe.db.get_value("Desktop Icon", {"label": label}, "name")
					if icon:
						icon_doc = frappe.get_doc("Desktop Icon", icon)
						updated = False
						
						# Update fields from JSON if they differ
						fields_to_update = ["app", "logo_url", "standard", "icon", "icon_type", 
											"link_type", "link_to", "parent_icon", "hidden", "idx"]
						
						for field in fields_to_update:
							json_value = json_data.get(field)
							if json_value is not None and icon_doc.get(field) != json_value:
								icon_doc.set(field, json_value)
								updated = True
						
						if updated:
							icon_doc.save(ignore_permissions=True)
				except Exception as e:
					frappe.log_error(
						title=_("Error updating icon from JSON"),
						message=_("Failed to update icon {0} from JSON: {1}").format(label, str(e)),
					)

		frappe.db.commit()
	except Exception as e:
		error_msg = _("Error updating icons from JSON: {0}").format(str(e))
		errors.append(error_msg)
		frappe.log_error(
			title=_("Error updating icons from JSON"),
			message=_("Failed to update icons from JSON files: {0}").format(str(e)),
		)

	# Step 4: Update link_type for existing icons that have link_to but missing/wrong link_type
	# This ensures proper structure for icons imported from JSON or created by auto_generate
	try:
		# Find icons with link_to but missing or wrong link_type
		# Get all Link icons with link_to set
		all_link_icons = frappe.get_all(
			"Desktop Icon",
			filters={
				"icon_type": "Link",
				"link_to": ["!=", ""],
			},
			fields=["name", "link_to", "link_type"],
		)

		# Filter icons that need link_type update
		icons_to_update = [
			icon for icon in all_link_icons
			if not icon.get("link_type") or icon.get("link_type") in ["Workspace", "DocType"]
		]

		for icon in icons_to_update:
			try:
				icon_doc = frappe.get_doc("Desktop Icon", icon["name"])
				# Check if Workspace Sidebar exists for this link_to
				if frappe.db.exists("Workspace Sidebar", icon["link_to"]):
					icon_doc.link_type = "Workspace Sidebar"
					icon_doc.save(ignore_permissions=True)
			except Exception as e:
				frappe.log_error(
					title=_("Error updating link_type"),
					message=_("Failed to update link_type for icon {0}: {1}").format(icon.get("name", "unknown"), str(e)),
				)

		frappe.db.commit()
	except Exception as e:
		error_msg = _("Error updating link_type: {0}").format(str(e))
		errors.append(error_msg)
		frappe.log_error(
			title=_("Error updating link_type"),
			message=_("Failed to update link_type for desktop icons: {0}").format(str(e)),
		)

	# Step 5: Use standard auto_generate_icons_and_sidebar() to create missing icons
	# This creates icons from workspaces and apps that don't have JSON files
	from frappe.utils.install import auto_generate_icons_and_sidebar

	try:
		auto_generate_icons_and_sidebar()
	except Exception as e:
		error_msg = _("Error during auto-generation: {0}").format(str(e))
		errors.append(error_msg)
		frappe.log_error(
			title=_("Error during auto-generation"),
			message=_("Failed to auto-generate icons and sidebars: {0}").format(str(e)),
		)

	# Step 6: Remove broken icons - icons without logo_url, without parent, at top level
	# Only remove if there are no other icons for any workspace of the same app
	try:
		broken_icons = frappe.get_all(
			"Desktop Icon",
			filters={
				"logo_url": ["in", [None, ""]],
				"parent_icon": ["in", [None, ""]],
			},
			fields=["name", "label", "link_to", "app"],
		)

		for icon in broken_icons:
			try:
				# Determine app for this icon
				app = icon.get("app")
				
				# If no app in icon, try to get it from workspace or workspace_sidebar
				if not app and icon.get("link_to"):
					# Try workspace_sidebar first
					app = frappe.db.get_value("Workspace Sidebar", icon["link_to"], "app")
					# If not found, try workspace
					if not app:
						app = frappe.db.get_value("Workspace", icon["link_to"], "app")

				# If we found an app, check if there are other icons for any workspace of this app
				if app:
					# Get all workspaces for this app
					app_workspaces = frappe.get_all(
						"Workspace",
						filters={"app": app, "public": 1},
						pluck="name",
					)
					
					# Also check workspace_sidebar
					app_sidebars = frappe.get_all(
						"Workspace Sidebar",
						filters={"app": app},
						pluck="title",
					)
					
					# Combine workspace names and sidebar titles
					all_workspace_names = set(app_workspaces + app_sidebars)
					
					# Check if there are other icons for any of these workspaces
					other_icons_count = frappe.db.count(
						"Desktop Icon",
						filters={
							"link_to": ["in", list(all_workspace_names)],
							"name": ["!=", icon["name"]],
						},
					)
					
					# Only delete if there are other icons for this app's workspaces
					if other_icons_count > 0:
						frappe.delete_doc("Desktop Icon", icon["name"], force=True, ignore_permissions=True)
				else:
					# If no app found, delete it (orphaned icon)
					frappe.delete_doc("Desktop Icon", icon["name"], force=True, ignore_permissions=True)
			except Exception as e:
				frappe.log_error(
					title=_("Error deleting broken icon"),
					message=_("Failed to delete icon {0}: {1}").format(icon.get("name", "unknown"), str(e)),
				)

		frappe.db.commit()
	except Exception as e:
		error_msg = _("Error removing broken icons: {0}").format(str(e))
		errors.append(error_msg)
		frappe.log_error(
			title=_("Error removing broken icons"),
			message=_("Failed to remove broken icons: {0}").format(str(e)),
		)

	# Clear cache again
	frappe.cache.delete_key("desktop_icons")

	# Count results
	total_icons = frappe.db.count("Desktop Icon")
	total_standard_icons = frappe.db.count("Desktop Icon", filters={"standard": 1})

	result = {
		"total_icons": total_icons,
		"total_standard": total_standard_icons,
		"errors": errors if errors else None,
	}

	return result
