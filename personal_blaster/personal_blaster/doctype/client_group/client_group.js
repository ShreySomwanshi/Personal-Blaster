// Copyright (c) 2022, Novacept and contributors
// For license information, please see license.txt

frappe.ui.form.on('Client Group', {

	refresh: function(frm) {
	        frm.add_custom_button(__('Update List'), function() {
        	frm.set_value('clients', []);
	        frappe.call({
			doc: frm.doc,
			method: 'filter',
			freeze: true,
			callback: function() {
				frm.reload_doc();

			}
		});
	});
    }
});
//		refresh: function(frm) {
//			frm.trigger('add_post_button');
//
//},
//	add_post_button : function(frm) {
//			frm.add_custom_button(__('Update Group'), function() {
  //      	                frappe.call({
    //            	                doc: frm.doc,
      //                  	        method: 'filter',
        //                        	freeze: true,
          //                      	callback: function() {
//                                        	frm.reload_doc();
//                               }
//
  //                      });
    //            });


// }
//});
