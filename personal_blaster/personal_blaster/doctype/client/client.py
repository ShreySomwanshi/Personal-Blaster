# Copyright (c) 2022, Novacept and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import append_number_if_name_exists

class Client(Document):
	def autoname(self):
		self.name = self.customer_name
		if frappe.db.exists("Client", self.name):
			self.name = append_number_if_name_exists("Client", self.name)

	def after_insert(self):
		self.contact()
	def contact(self):
		print('update')
		if frappe.db.exists("Customer",self.customer_name):
			doc = frappe.get_doc("Customer",self.customer_name)
		else:
			doc = doc = frappe.new_doc('Customer')
		doc.customer_name = self.customer_name
		doc.customer_group = 'Commercial'
		doc.territory = 'All Territories'
		doc.mobile_no = self.mobile_no
		doc.email_id = self.email_id
		print(doc)
		doc.save()

		if self.add_1:
			if frappe.db.exists("Address",f"{self.customer_name}-Billing"):
				add_doc = frappe.get_doc("Address",f"{self.customer_name}-Billing")
			else:
				add_doc = frappe.new_doc("Address")
			add_doc.address_title = self.customer_name
			add_doc.address_line1 = self.add_1
			add_doc.address_line2 = self.add_2
			add_doc.city = self.city
			add_doc.state = self.state
			add_doc.country = self.country
			add_doc.pincode = self.pincode
			add_doc.save()
		print('DONE')
	def validate(self):
		self.set_primary_email()
		self.set_primary("phone")
		self.set_primary("mobile_no")
#s		self.contact()
	def set_primary_email(self):
		if not self.email_ids:
			self.email_id = ""
			return

		if len([email.email_id for email in self.email_ids if email.is_primary]) > 1:
			frappe.throw(("Only one {0} can be set as primary.").format(frappe.bold("Email ID")))

		primary_email_exists = False
		for d in self.email_ids:
			if d.is_primary == 1:
				primary_email_exists = True
				self.email_id = d.email_id.strip()
				break

		if not primary_email_exists:
			self.email_id = ""


	def set_primary(self, fieldname):
		# Used to set primary mobile and phone no.
		if len(self.phone_nos) == 0:
			setattr(self, fieldname, "")
			return

		field_name = "is_primary_" + fieldname

		is_primary = [phone.phone for phone in self.phone_nos if phone.get(field_name)]
		print(is_primary)
		if len(is_primary) > 1:
			frappe.throw(("Only one {0} can be set as primary.").format(frappe.bold(frappe.unscrub(fieldname))))

		primary_number_exists = False
		for d in self.phone_nos:
			if d.get(field_name) == 1:
				primary_number_exists = True
				setattr(self, fieldname, d.phone)
				break

		if not primary_number_exists:
			setattr(self, fieldname, "")


	def on_update(self):
		# Update customer and contact
		pass



#	Syncing Contact to messagebird

