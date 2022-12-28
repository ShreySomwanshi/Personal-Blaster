# Copyright (c) 2022, Novacept and contributors
# For license information, please see license.txt

#import frappe
#from frappe.model.document import Document

#class WhatsappTemplate(Document):
#	def validate(self):
#		frappe.throw(('Whatsapp Template Not saved'))
import frappe
from frappe.model.document import Document
import requests
import json
from frappe import _
import re
class WhatsappTemplate(Document):


	def validate(self):
	#	frappe.throw((f'Error'))
		if not frappe.db.get_single_value('Whatsapp Setting','access_token'):
			frappe.throw(_('Setup Whatsapp Configuration to create Template'))

		self.name_validation()
		self.validate_placeholder()
		global status
		status = ''
		status = self.get_status()

		if status:
			pass
		else:
			frappe.throw(_("Something is incorrect with 'Whatsapp Setting'"))


	def name_validation(self):
		name = self.temp_name
		syntax = r"(?:[a-z]|[0-9]|[_])+"
		result = re.findall(syntax,name)
		if len(result) >1 or result[0] != name:
			frappe.throw(_("Name should contain lowercase letters, numbers and underscores only"))

	def get_status(self):

		access_token_doc = frappe.get_doc('Whatsapp Setting')
		access_token = access_token_doc.get_password('access_token')

		try:
			print('loop')
			if self.button:
				response = self.create_template_buttons(self.button_1,self.button_2,self.temp_name)
			else:
				response = self.create_template(self.temp_name)
			print(response)
			response = json.loads(response)
			status = response['status'].capitalize()
			return status
		except:
			pass

	def create_template_buttons(self,first_button,second_button,name):
		url = "https://integrations.messagebird.com/v2/platforms/whatsapp/templates"

		payload = json.dumps({
		"language": "en",
		"components": [
			self.api_body(),
			{
				"type": "BUTTONS",
				"buttons": [
					{
						"type": "QUICK_REPLY",
						"text": first_button
					},
					{
						"type": "QUICK_REPLY",
						"text": second_button
					}
				]
			}
			],
			"name": name,
			"category": "TRANSACTIONAL"
		})
		headers = self.get_header()
#			'Authorization': f'AccessKey {access}',
#			'Content-Type': 'application/json'
#		}

		response = requests.request("POST", url, headers=headers, data=payload)

		return response.text



	def create_template(self,name):
		url = "https://integrations.messagebird.com/v2/platforms/whatsapp/templates"

		payload = json.dumps({
		"language": "en",
		"components": [
			self.api_body(),
			],
			"name": name,
			"category": "TRANSACTIONAL"
		})
		headers = self.get_header()
#			'Authorization': f'AccessKey {access}',
#			'Content-Type': 'application/json'
#		}


		print(payload)
		response = requests.request("POST", url, headers=headers, data=payload)

		return response.text

	def after_insert(self):

		frappe.db.set_value('Whatsapp Template', self.name ,'temp_status', status)
		frappe.db.commit()

	def api_body(self):
		body_list = []
		message = {"type": "BODY","text": self.message}
		if self.field_list:

#			example_tuple = frappe.db.get_list('Whatsapp Placeholder',filters={"parent":self.name},fields=["field_example"],as_list = 1)

			example_list = []
			examples = []
			for entry in self.field_list:
				example_list.append(entry.field_example)
			examples.append(example_list)
			example_dict = {"example":{"body_text": examples}}
			message.update(example_dict)
		return message

	def get_header(self):
		access_token_doc = frappe.get_doc('Whatsapp Setting')
		access_token = access_token_doc.get_password('access_token')

		header = {'Authorization': f'AccessKey {access_token}','Content-Type': 'application/json'}
		return header


	@frappe.whitelist()
	def update_status(self):

		access_token_doc = frappe.get_doc('Whatsapp Setting')
		access_token = access_token_doc.get_password('access_token')

		url = f"https://integrations.messagebird.com/v2/platforms/whatsapp/templates/{self.name}"

		payload={}
		headers = {
			'Authorization': f'AccessKey {access_token}',
			'Content-Type': 'application/json'
		}

		response = requests.request("GET", url, headers=headers, data=payload)
		status =  json.loads(response.text)[0]['status']
		self.db_set("temp_status", status.capitalize())
		frappe.db.commit()

	@frappe.whitelist()
	def delete_temp(self):
		access_token_doc = frappe.get_doc('Whatsapp Setting')
		access_token = access_token_doc.get_password('access_token')

		url = f"https://integrations.messagebird.com/v2/platforms/whatsapp/templates/{self.name}"

		payload={}
		headers = {
			'Authorization': f'AccessKey {access_token}',
			'Content-Type': 'application/json'
		}
		print(headers)
		response = requests.request("DELETE", url, headers=headers, data=payload)

		if response.text:
			frappe.throw((response.text))
		else:
			frappe.msgprint(('Deleted'))
			self.db_set("temp_status", 'Deleted')
			frappe.db.commit()

	def validate_placeholder(self):
		integers = []
		place_holder = re.findall('{{\d+}}',self.message)
		place_values = self.field_list

		if not place_holder and not self.field_list:
			return
		elif place_holder and self.field_list:
			pass
		else:
			frappe.throw(_('Equal placeholders and their field values both should be given'))

		print('Test1')
		for num in place_holder:
			integers.append(int(num[2:-2]))

		if integers != list(range(1,1+len(integers))):
			frappe.throw(_('All variables must be numeric and variables must increment, with your first variable being {{1}}'))

		if len(integers) != len(place_values):
			frappe.throw(_('There should be equal placeholders and field values'))

#		fields = frappe.db.get_list('Whatsapp Placeholder',filters={"parent":self.name},fields=["field"],as_list = 1)
#		print('Test2')
		doc = frappe.get_last_doc('Client')
#		print('FIELD')
#		print(fields)
		for entry in self.field_list:


#		for i in range(len(fields)):
			try:
				values = frappe.db.get_value('Client',doc.name,entry.field)
			except:
				frappe.throw(_(f"Client document has no value called {entry.field}"))

	@frappe.whitelist()
	def print_msg(self):
		frappe.msgprint(('Success'))
