# Copyright (c) 2022, Novacept and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ClientGroup(Document):

	def validate(self):
		if not self.interest and not self.city and not self.country:
			frappe.throw(_('All fields cannot be empty'))

	@frappe.whitelist()
	def filter(self):
		city_list = {}
		interest_list = {}
		country_list = {}
#		filter_list = [set(city_list),set(interest_list),set(country_list)]

		if self.interest:
			interest_list = frappe.db.get_list('Interests',filters={'Interest':self.interest},fields=['parent'],as_list=1)
		if self.city:
			city_list = frappe.db.get_list('Client',filters={'City':self.city},as_list=1)
		if self.country:
			country_list = frappe.db.get_list('Client',filters={'Country':self.country},as_list=1)

		filter_list = [set(city_list),set(interest_list),set(country_list)]
		non_empty_list = [x for x in filter_list if x]
		print(non_empty_list)
		if not non_empty_list:
			frappe.throw((f'No contacts added'))
			return
		final_list = set.intersection(*non_empty_list)
		print(final_list)
		for i in final_list:
			self.append("clients",{"client_member":i[0]})
			print(i[0])
		self.save()
		frappe.msgprint((f'{len(final_list)} contacts added'))
