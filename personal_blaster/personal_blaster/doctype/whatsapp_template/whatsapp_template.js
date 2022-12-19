// Copyright (c) 2022, Novacept and contributors
// For license information, please see license.txt

//frappe.ui.form.on('Whatsapp Template', {
	// refresh: function(frm) {

	// }
//});

frappe.ui.form.on('Whatsapp Template', {
        refresh: function(frm) {
                frm.add_custom_button(__('Update Status'), function() {
                        frappe.call({
                                doc: frm.doc,
                                method: 'update_status',
                                freeze: true,
                                callback: function() {
                                        frm.reload_doc();
                                }
                        });
                });

		frm.add_custom_button(__('Delete Template'), function() {
                        frappe.call({
                                doc: frm.doc,
                                method: 'delete_temp',
                                freeze: true,
                                callback: function() {
                                        frm.reload_doc();
                                }
                        });
                });

	}

});
