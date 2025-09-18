// Copyright (c) 2025, Gameplan and contributors
// For license information, please see license.txt

frappe.ui.form.on('GP Notification Log', {
	refresh: function(frm) {
		// Add custom buttons
		if (frm.doc.is_read) {
			frm.add_custom_button(__('Mark as Unread'), function() {
				frm.set_value('is_read', 0);
				frm.set_value('read_at', '');
				frm.save();
			});
		} else {
			frm.add_custom_button(__('Mark as Read'), function() {
				frm.set_value('is_read', 1);
				frm.set_value('read_at', frappe.datetime.now_datetime());
				frm.save();
			});
		}

		// Add button to view reference document
		if (frm.doc.reference_doctype && frm.doc.reference_name) {
			frm.add_custom_button(__('View Reference'), function() {
				frappe.set_route('Form', frm.doc.reference_doctype, frm.doc.reference_name);
			});
		}
	},

	notification_type: function(frm) {
		// Set default title based on notification type
		if (!frm.doc.title) {
			const type_titles = {
				'Task Assignment': 'New Task Assignment',
				'Task Status Change': 'Task Status Updated',
				'Task Movement': 'Task Moved',
				'Project Update': 'Project Updated',
				'Discussion': 'New Discussion',
				'Comment': 'New Comment',
				'System': 'System Notification',
				'Custom': 'Custom Notification'
			};
			frm.set_value('title', type_titles[frm.doc.notification_type] || 'Notification');
		}
	}
});
