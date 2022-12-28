// Copyright (c) 2022, Novacept and contributors
// For license information, please see license.txt

frappe.ui.form.on('Whatsapp Post', {
	// refresh: function(frm) {

	// }
	refresh: function(frm) {
		if (frm.doc.post_status !== 'Posted')
		frm.add_custom_button(__('Posts Now'), function() {
                        frappe.call({
                               // doc: frm.doc,
                                method: 'personal_blaster.personal_blaster.doctype.whatsapp_post.whatsapp_post.process_scheduled_whatsapp_message',
                                freeze: true,
                                callback: function() {
                                        frm.reload_doc();
                                }
                        });
                });
	}

});
