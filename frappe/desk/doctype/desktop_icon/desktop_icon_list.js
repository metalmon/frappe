frappe.listview_settings["Desktop Icon"] = {
	onload: function (listview) {
		listview.page.add_menu_item(__("Reset All Desktop Icons"), function () {
			frappe.confirm(
				__(
					"This will delete all standard desktop icons and recreate them from installed apps and workspaces. This is useful when app titles have changed in hooks. Continue?"
				),
				function () {
					frappe.call({
						method: "frappe.desk.doctype.desktop_icon.desktop_icon_reset.reset_all_desktop_icons",
						freeze: true,
						freeze_message: __("Resetting desktop icons..."),
						callback: function (r) {
							if (r.exc) {
								frappe.msgprint({
									title: __("Error"),
									message: r.exc,
									indicator: "red",
								});
							} else if (r.message) {
								let message = __("Desktop icons reset successfully.");
								if (r.message.deleted !== undefined) {
									message += " " + __("Deleted: {0}", [r.message.deleted]);
								}
								if (r.message.files_found !== undefined) {
									message += " " + __("Files found: {0}", [r.message.files_found]);
									if (r.message.apps_with_files) {
										message += " (" + __("from: {0}", [r.message.apps_with_files]) + ")";
									}
								}
								if (r.message.imported_from_files !== undefined) {
									message += " " + __("Imported from files: {0}", [r.message.imported_from_files]);
								}
								if (r.message.auto_created !== undefined) {
									message += " " + __("Auto-created: {0}", [r.message.auto_created]);
								}
								if (r.message.total_created !== undefined) {
									message += " " + __("Total created: {0}", [r.message.total_created]);
								}
								if (r.message.errors && r.message.errors.length > 0) {
									frappe.msgprint({
										title: __("Reset completed with errors"),
										message: message + "<br><br>" + r.message.errors.join("<br>"),
										indicator: "orange",
									});
								} else {
									frappe.show_alert({
										message: message,
										indicator: "green",
									});
								}
								// Refresh list
								listview.refresh();
							}
						},
					});
				}
			);
		});
	},
};
