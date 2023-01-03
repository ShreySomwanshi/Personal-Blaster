# Copyright (c) 2022, Novacept and contributors
# For license information, please see license.txt

from frappe import _
import frappe
from frappe.model.document import Document
from frappe.model.naming import append_number_if_name_exists
import requests
import json
from frappe.utils import cint, cstr, flt, get_formatted_email, today
#messagebird_url = "https://rest.messagebird.com/contacts/"
class Client(Document):
	def autoname(self):
		self.name = self.get_customer_name()

	def get_customer_name(self):

		if frappe.db.get_value("Client", self.customer_name) and not frappe.flags.in_import:
			count = frappe.db.sql(
				"""select ifnull(MAX(CAST(SUBSTRING_INDEX(name, ' ', -1) AS UNSIGNED)), 0) from tabClient
				 where name like %s""",
				"%{0} - %".format(self.customer_name),
				as_list=1,
			)[0][0]
			count = cint(count) + 1

			new_customer_name = "{0} - {1}".format(self.customer_name, cstr(count))

			frappe.msgprint(
				_("Changed customer name to '{}' as '{}' already exists.").format(
					new_customer_name, self.customer_name
				),
				title=_("Note"),
				indicator="yellow",
			)

			return new_customer_name

		return self.customer_name


	def contact(self):
		print('update')
		if self.linked_customer:
			doc = frappe.get_doc("Customer",self.linked_customer)

		elif self.email_id and frappe.db.exists("Customer",{"email_id":self.email_id}):
			doc = frappe.get_doc("Customer",frappe.db.exists("Customer",{"email_id":self.email_id}))

		elif self.mobile_no and frappe.db.exists("Customer",{"mobile_no":self.mobile_no}):
			doc = frappe.get_doc("Customer",frappe.db.exists("Customer",{"mobile_no":self.mobile_no}))

		else:
			doc = frappe.new_doc('Customer')
		doc.customer_name = self.customer_name
		doc.customer_group = 'Commercial'
		doc.territory = 'All Territories'
		doc.save()
		if self.mobile_no or self.email_id:
			if self.linked_address:
				print('link')
				contact_doc = frappe.get_doc("Contact",self.linked_contact)
			elif frappe.db.exists("Contact",{"email_id":self.email_id}):
				print('email')
				contact_doc = frappe.get_doc("Contact",frappe.db.exists("Contact",{"email_id":self.email_id}))

			elif frappe.db.exists("Contact",{"mobile_no":self.mobile_no}):
				print('mobile')
				contact_doc = frappe.get_doc("Contact",frappe.db.exists("Contact",{"mobile_no":self.mobile_no}))
			else:
				print('new')
				contact_doc = frappe.new_doc('Contact')
			contact_doc.first_name = self.customer_name

			if contact_doc.mobile_no:
				frappe.db.delete('Contact Phone',{"parent":contact_doc.name})
				contact_doc.mobile_no = None

			if contact_doc.email_id:
				frappe.db.delete('Contact Email',{"parent":contact_doc.name})
				contact_doc.email_id = None
			print('1')
#			contact_doc.reload()
			contact_doc.save()
			contact_doc.reload()
			if self.mobile_no:
				contact_doc.append("phone_nos",{"phone":self.mobile_no,"is_primary_mobile_no":1})
			if self.email_id:
				contact_doc.append("email_ids",{"email_id":self.email_id,"is_primary":1})
			print('2')
			contact_doc.append("links",{"link_doctype":"Customer","link_name":doc.name})
			contact_doc.save()

			if not self.linked_contact:
				self.db_set('linked_contact',contact_doc.name)
			doc.reload()
			doc.customer_primary_contact = contact_doc.name
			doc.save()
			print('3')

		if self.add_1:
			if self.linked_address:
				add_doc = frappe.get_doc("Address",self.linked_address)

			elif frappe.db.exists("Address",f"{self.name}-Billing"):
				add_doc = frappe.get_doc("Address",f"{self.customer_name}-Billing")
			else:
				add_doc = frappe.new_doc("Address")
			add_doc.address_title = self.name
			add_doc.address_line1 = self.add_1
			add_doc.address_line2 = self.add_2
			add_doc.city = self.city
			add_doc.state = self.state
			add_doc.country = self.country
			add_doc.pincode = self.pincode
			add_doc.append("links",{"link_doctype":"Customer","link_name":doc.name})

			add_doc.save()
			if not self.linked_address:
				self.db_set('linked_address',add_doc.name)
			doc.reload()
			doc.customer_primary_address = add_doc.name
			doc.save()


		if not self.linked_customer:
			self.db_set('linked_customer',doc.name)

		print('DONE')
	def validate(self):
		pass
#		print('validate')
#		self.set_primary_email()
#		self.set_primary("phone")
#		self.set_primary("mobile_no")
#		self.contact()
#		self.update_messagebird()
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
		print('update')
		self.update_to_messagebird()
		self.contact()


	@frappe.whitelist()
	def upload_to_messagebird(self):
#		token_doc = frappe.get_doc('Whatsapp Setting')
#		token = token_doc.get_password('access_token')
#		if not token:
#			frappe.throw(_('Access token is not Configured'))
		url = self.messagebird_url()

		payload=json.dumps({
			'msisdn':self.mobile_no,'firstName':self.customer_name
		})
		headers = self.get_header()

		response = requests.request("POST", url, headers=headers, data=payload)
		print(response.text)

		try:
			messagebird_contact_id = json.loads(response.text)['id']
			self.db_set("client_id",messagebird_contact_id)
			self.db_set("contact_status","UPLOADED")
			frappe.msgprint(_("Contact Uploaded successfully"))
		except:

			self.contact_status = 'ERROR'
			frappe.msgprint(_('Error in uploading contact'))

		#print(headers)
		return response.text

	def get_header(self):
		token_doc = frappe.get_doc('Whatsapp Setting')
		token = token_doc.get_password('access_token')
		if not token:
			frappe.throw(_('Access token is not Configured'))

		headers = {
		  'Authorization': f'AccessKey {token}',
		  'Content-Type': 'application/json'
		}
		return headers
	def update_to_messagebird(self):
		if self.contact_status == "UPLOADED" and self.mobile_no and self.client_id:
			url = self.messagebird_url() + self.client_id
			headers = self.get_header()
			print(headers)
			payload = ""
			response = requests.request("GET",url,headers=headers,data = payload)
			msisdn = json.loads(response.text)
#['msisdn']
			if msisdn == self.mobile_no:
				pass
			else:
				payload = json.dumps({
					'msisdn':self.mobile_no
				})
				response = requests.request("PATCH", url, headers=headers, data=payload)
				print('Contact Updated')
		elif not self.mobile_no and self.contact_status == "UPLOADED":
			self.delete_from_messagebird()

	def delete_from_messagebird(self):
		if self.contact_status != 'UPLOADED' or not self.client_id:
			return
		url = self.messagebird_url() + self.client_id
		headers = self.get_header()
		payload =""
		response = requests.request("DELETE",url,headers=headers,data = payload)
		if response.text:
			frappe.throw(_('Problem is Deleting the Client'))
		print(response.text)
		self.db_set('contact_status','NOT UPLOADED')
		self.db_set('client_id','')
		print('Contact Deleted')

	def on_trash(self):
		self.delete_from_messagebird()

	def messagebird_url(self):
		messagebird_url = "https://rest.messagebird.com/contacts/"
		return messagebird_url




@frappe.whitelist()
def upload_all_contacts():

	unuploaded_client_list = frappe.get_list('Client',filters={'contact_status':'NOT UPLOADED'},as_list=1)

	for i in range(len(unuploaded_client_list)):
		try:
			client_doc = frappe.get_doc('Client',unuploaded_client_list[i][0])
			number_id = client_doc.upload_to_messagebird()
			#number_id = json.loads(number_id)['id']
		except:
			pass

def update_all_client():
	import datetime
	contacts = frappe.db.get_list('Contact',fields=['name','modified'])

	print('List of Contacts')
	print(contacts)
	print('\n\n')
	for contact in contacts:
#		print(f'Contact: {contact}')
#		print('\n')
		if contact['modified'] > frappe.utils.now_datetime() - datetime.timedelta(minutes = 65):
			print(f'{contact} modified')
			client_modified = frappe.db.get_value('Client',{'linked_contact':contact['name']},'modified')
			print(client_modified)
			if client_modified and contact['modified'] > client_modified:
				client_name = frappe.db.get_value('Client',{'linked_contact':contact['name']},'name')

				print(client_name)
				frappe.db.set_value('Client',client_name,'mobile_no',frappe.db.get_value('Contact',contact['name'],'mobile_no'))
				frappe.db.set_value('Client',client_name,'email_id',frappe.db.get_value('Contact',contact['name'],'email_id'))
				frappe.db.commit()
				client = frappe.get_doc('Client',client_name)
				client.update_to_messagebird()

	addresses = frappe.db.get_list('Address',fields=['name','modified'])
	for address in addresses:
		if address['modified'] > frappe.utils.now_datetime() - datetime.timedelta(hours=6):
			client_modified = frappe.db.get_value('Client',{'linked_address':address['name']},'modified')
			if client_modified and address['modified'] > client_modified:

				client_name = frappe.db.get_value('Client',{'linked_address':contact['name']},'name')
				frappe.db.set_value('Client',client_name,'add_1',frappe.db.get_value('Address',address['name'],'address_line1'))
				frappe.db.set_value('Client',client_name,'add_2',frappe.db.get_value('Address',address['name'],'address_line2'))
				frappe.db.set_value('Client',client_name,'city',frappe.db.get_value('Address',address['name'],'city'))
				frappe.db.set_value('Client',client_name,'state',frappe.db.get_value('Address',address['name'],'state'))
				frappe.db.set_value('Client',client_name,'country',frappe.db.get_value('Address',address['name'],'country'))
				frappe.db.set_value('Client',client_name,'pincode',frappe.db.get_value('Address',address['name'],'pincode'))
				frappe.db.commit()
