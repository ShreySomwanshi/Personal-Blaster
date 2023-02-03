# Copyright (c) 2022, Novacept and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
class ClientGroup(Document):

	def validate(self):
		if not self.interests and not self.cities and not self.countries:
			frappe.throw(_('All fields cannot be empty'))

	@frappe.whitelist()
	def filter(self):
		city_list = ()
		interest_list = ()
		country_list = ()
		industry_list = ()
		market_segment = ()
		title_list = ()

		filter_list = []

		if self.interests:
			interests = frappe.db.get_list('Client',fields=['name','`tabInterests`.`Interest`'],as_list=1)
			print(interests)
			in_list = []
			for i in interests:
				in_list.append(list(i))
			print(in_list)
			interest_list = []
			if self.interest_logic=='OR':
				for j in self.interests:
					for i in in_list:
						if i[1] == j.interest:
							value = []
							value.append(i[0])
							try:
								interest_list.append(tuple(value))
							except:
								pass
				print(interest_list)
				interest_list = tuple(interest_list)
				filter_list.append(set(interest_list))
			else:
				for j in self.interests:
					if len(interest_list) > 0:
						test = []
						for i in in_list:
							if i[1] == j.interest and (i[0],) in interest_list:
								value = []
								value.append(i[0])
								try:
									test.append(tuple(value))
								except:
									pass
						interest_list = test
					else:
						for i in in_list:
							if i[1] == j.interest:
								value = []
								value.append(i[0])
								try:
									interest_list.append(tuple(value))
								except:
									pass   
			interest_list = tuple(interest_list)
			if len(interest_list) > 0:
    				filter_list.append(set(interest_list))
			print(interest_list)
			print(filter_list)
		if self.cities:
			for i in self.cities:
				city_list += frappe.db.get_list('Client',filters={'City':i.city},as_list=1)
			filter_list.append(set(city_list))
			print(city_list)
			print(filter_list)
		if self.countries:
			for i in self.countries:
				country_list += frappe.db.get_list('Client',filters={'Country':i.countries},as_list=1)
			filter_list.append(set(country_list))
			print(country_list)
			print(filter_list)
		
		if self.industry:
			for i in self.industry:
				industry_list += frappe.db.get_list('Client',filters={'Industry':i.industry},as_list=1)
			filter_list.append(set(industry_list))
			print(industry_list)
			print(filter_list)
		if self.market_segment:
			for i in self.market_segment:
				market_segment += frappe.db.get_list('Client',filters={'Market_Segment':i.market_segment},as_list=1)
			filter_list.append(set(market_segment))
			print(market_segment)
			print(filter_list)
		if self.job_title:
			for i in self.job_title:
				title_list += frappe.db.get_list('Client',filters={'Job_Title':i.job_title},as_list=1)
			filter_list.append(set(title_list))
			print(title_list)
			print(filter_list)
		
#		filter_list = [set(city_list),set(interest_list),set(country_list)]
		non_empty_list = [x for x in filter_list]
		print(non_empty_list)
		if not non_empty_list:
			frappe.throw((f'No contacts added'))
			return
		if self.filter_logic=='AND':
			final_list = set.intersection(*non_empty_list)
		else:
			final_list = set.union(*non_empty_list)
		print(final_list)
		for i in final_list:
			self.append("clients",{"client_member":i[0]})
			print(i[0])
		self.save()
		frappe.msgprint((f'{len(final_list)} contacts added'))
