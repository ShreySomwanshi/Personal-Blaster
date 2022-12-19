// Copyright (c) 2022, Novacept and contributors
// For license information, please see license.txt

frappe.ui.form.on('Client', {
//	refresh: function(frm) {
//		if (frm.doc.contact_status === 'NOT UPLOADED')
//			{
//			frm.trigger('add_upload_btn');
//
//			}
//	}
//	add_upload_btn: function(frm) {
      //          frm.add_custom_button(__('Upload'), function() {
    //                    frappe.call({
  //                              doc: frm.doc,
//                                method: 'upload_to_messagebird',
              //                  freeze: true,
            //                    callback: function() {
          //                              frm.reload_doc();
        //                        }
      //                  });
    //            });
  //      }
//});

//frappe.ui.form.on('Whatsapp Template', {
        refresh: function(frm) {
		if (frm.doc.contact_status === 'NOT UPLOADED')
                frm.add_custom_button(__('Upload Contact'), function() {
                        frappe.call({
                                doc: frm.doc,
                                method: 'upload_to_messagebird',
                                freeze: true,
                                callback: function() {
                                        frm.reload_doc();
                                }
                        });
                });
	}

});
