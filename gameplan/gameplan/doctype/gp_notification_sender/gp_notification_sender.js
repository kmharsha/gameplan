// Copyright (c) 2025, Gameplan and contributors
// For license information, please see license.txt

frappe.ui.form.on('GP Notification Sender', {
	refresh: function(frm) {
		// Add custom buttons
		if (frm.doc.status === 'Draft' && frm.doc.send_immediately) {
			frm.add_custom_button(__('Send Now'), function() {
				frm.call('send_notification').then(() => {
					frm.reload_doc();
				});
			});
		}

		if (frm.doc.status === 'Draft' && !frm.doc.send_immediately && frm.doc.scheduled_time) {
			frm.add_custom_button(__('Schedule'), function() {
				frm.call('schedule_notification').then(() => {
					frm.reload_doc();
				});
			});
		}

		// Add button to view reference document
		if (frm.doc.reference_doctype && frm.doc.reference_name) {
			frm.add_custom_button(__('View Reference'), function() {
				frappe.set_route('Form', frm.doc.reference_doctype, frm.doc.reference_name);
			});
		}

		// Add test notification button
		frm.add_custom_button(__('Send Test'), function() {
			frappe.call({
				method: 'gameplan.api.notifications.test_notification',
				callback: function(r) {
					if (r.message) {
						frappe.msgprint(__('Test notification sent successfully'));
					}
				}
			});
		});
	},

	send_immediately: function(frm) {
		if (frm.doc.send_immediately) {
			frm.set_value('scheduled_time', '');
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
	},

	recipient_user: function(frm) {
		if (frm.doc.recipient_user) {
			frm.set_value('recipient_role', '');
		}
	},

	recipient_role: function(frm) {
		if (frm.doc.recipient_role) {
			frm.set_value('recipient_user', '');
		}
	}
});
