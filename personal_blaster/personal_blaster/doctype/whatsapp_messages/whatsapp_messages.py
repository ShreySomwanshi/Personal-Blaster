# Copyright (c) 2022, Novacept and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class WhatsappMessages(Document):
	def on_update(self):
		self.status_update_time = frappe.utils.now_datetime()
		sent = len(frappe.db.get_values("Whatsapp Messages",{'campaign':self.campaign,'status':'SENT'}, 'name', as_dict=1))
		read = len(frappe.db.get_values("Whatsapp Messages",{'campaign':self.campaign,'status':'READ'}, 'name', as_dict=1))
		failed = len(frappe.db.get_values("Whatsapp Messages",{'campaign':self.campaign,'status':'FAILED'}, 'name', as_dict=1))
		rejected = len(frappe.db.get_values("Whatsapp Messages",{'campaign':self.campaign,'status':'REJECTED'}, 'name', as_dict=1))
		all = len(frappe.db.get_values("Whatsapp Messages",{'campaign':self.campaign}, 'name', as_dict=1))
		accepted = len(frappe.db.get_values("Whatsapp Messages",{'campaign':self.campaign,'status':'ACCEPTED'}, 'name', as_dict=1))
		transmitted = len(frappe.db.get_values("Whatsapp Messages",{'campaign':self.campaign,'status':'TRANSMITTED'}, 'name', as_dict=1))
		pending = len(frappe.db.get_values("Whatsapp Messages",{'campaign':self.campaign,'status':'PENDING'}, 'name', as_dict=1))
		delivered = len(frappe.db.get_values("Whatsapp Messages",{'campaign':self.campaign,'status':'DELIVERED'}, 'name', as_dict=1))


		doc = frappe.get_doc('Whatsapp Post',self.campaign)
		doc.msg_sent = sent
		doc.msg_read = read
		doc.msg_delivered = delivered
		doc.msg_accepted = accepted
		doc.msg_transmitted = transmitted
		doc.msg_pending = pending
		doc.msg_failed = failed
		doc.msg_rejected = rejected
		doc.msg_total = all
		doc.save()
