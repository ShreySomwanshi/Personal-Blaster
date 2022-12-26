# Copyright (c) 2022, Novacept and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

import frappe
from frappe import _
from frappe.core.doctype.communication.email import make
from frappe.model.document import Document
from frappe.utils import add_days, getdate, today, get_datetime
import datetime

class NovaceptEmailPost(Document):
	def validate(self):
		self.set_date()
		self.trial()
		# checking if email is set for lead. Not checking for contact as email is a mandatory field for contact.
		if self.email_campaign_for == "Lead":
			self.validate_lead()
		self.validate_email_camp_already_exists()
		self.update_status()

	def set_date(self):
		print(f'\n\n\nCurrent\n{frappe.utils.now_datetime() + datetime.timedelta(seconds = 30)}\n\n\n\n')
		print(f'\n\n\n\nStart{frappe.utils.get_datetime(self.start_date)}\n\n\n\n')
		if  frappe.utils.get_datetime(self.start_date) <(frappe.utils.now_datetime()) :
			frappe.throw(_("Scheduled Time must be a future time."))
		# set the end date as start date + max(send after days) in campaign schedule
		send_after_days = []
		campaign = frappe.get_doc("Campaign", self.campaign_name)
		for entry in campaign.get("campaign_schedules"):
			send_after_days.append(entry.send_after_days)
		try:
			self.end_date = add_days(frappe.utils.get_datetime(self.start_date), max(send_after_days))
		except ValueError:
			frappe.throw(
				_("Please set up the Campaign Schedule in the Campaign {0}").format(self.campaign_name)
			)

	def validate_lead(self):
		lead_email_id = frappe.db.get_value("Lead", self.recipient, "email_id")
		if not lead_email_id:
			lead_name = frappe.db.get_value("Lead", self.recipient, "lead_name")
			frappe.throw(_("Please set an email id for the Lead {0}").format(lead_name))

	def trial(self):
		print(self.last_post_time)
		self.last_post_time = frappe.utils.now_datetime()
		print(self.last_post_time)
	def validate_email_camp_already_exists(self):
		email_camp_exists = frappe.db.exists(
			"Novacept Email Post",
			{
				"campaign_name": self.campaign_name,
				"recipient": self.recipient,
				"status": ("in", ["In Progress", "Scheduled"]),
				"name": ("!=", self.name),
			},
		)
		if email_camp_exists:
			frappe.throw(
				_("The Campaign '{0}' already exists for the {1} '{2}'").format(
					self.campaign_name, self.email_campaign_for, self.recipient
				)
			)
	def update_status(self):
		start_date = getdate(self.start_date)
		end_date = getdate(self.end_date)
		today_date = getdate(today())
		if start_date > today_date:
			self.status = "Scheduled"
		elif end_date >= today_date:
			self.status = "In Progress"
		elif end_date < today_date:
			self.status = "Completed"

	def update_post_status(self):
		frappe.db.set_value("Novacept Email Post",self.name,"last_post_time",frappe.utils.now_datetime())
		frappe.db.commit()

# called through hooks to send campaign mails to leads
def send_email_to_leads_or_contacts():
	print('start')
	email_campaigns = frappe.get_all(
		"Novacept Email Post", filters={"status": ("not in", ["Unsubscribed", "Completed", "Scheduled"])}
	)
	print(email_campaigns)
	for camp in email_campaigns:
		email_camp = frappe.get_doc("Novacept Email Post", camp.name)
		last_post = email_camp.get("last_post_time")
		campaign = frappe.get_cached_doc("Campaign", email_camp.campaign_name)
		for entry in campaign.get("campaign_schedules"):
			scheduled_date = add_days(email_camp.get("start_date"), entry.get("send_after_days"))
#			last_post = email_camp.get("last_post_time")
			if last_post < scheduled_date < frappe.utils.now_datetime():
				send_mail(entry, email_camp)
				email_camp.update_post_status()
def send_mail(entry, email_camp):

	# MS 365 config
	client_id = '50c30077-9943-431d-ab29-bbde17ee758d'
	client_secret = '_zr8Q~qsf0tQyH51pFLAsAFE1P2r71.JJc~k2bSm'
	tenant_id = '2403bce5-4dae-4017-bf88-e7951c2fc169'

	authority = f"https://login.microsoftonline.com/{tenant_id}"
	app = msal.ConfidentialClientApplication(client_id=client_id,client_credential=client_secret,authority=authority)
	scopes = ["https://graph.microsoft.com/.default"]


	result = None
	result = app.acquire_token_silent(scopes, account=None)

	if not result:
		print("No suitable token exists in cache. Let's get a new one from Azure Active Directory.")
		result = app.acquire_token_for_client(scopes=scopes)




	recipient_list = []
	if email_camp.email_campaign_for == "Client Group":
		group = frappe.get_doc(email_camp.email_campaign_for,email_camp.get('recipient'))
		for member in group.clients:
			if frappe.db.get_value('Client',member.client_member,'email_id'):
				recipient_list.append(frappe.db.get_value('Client',member.client_member,'email_id'))
	else:
		print(email_camp.email_campaign_for)
		print(email_camp.get("recipient"))
		print(email_camp)
		recipient_list.append(
			frappe.db.get_value(
				'Client',email_camp.get("recipient") ,"email_id"

			)
		)
	email_template = frappe.get_doc("Email Template", entry.get("email_template"))
	sender = email_camp.get("sender")


	if "access_token" in result:
		for recipient in recipient_list:
			endpoint = f'https://graph.microsoft.com/v1.0/users/{sender}/sendMail'
			email_msg = {
				'Message': {
					'Subject': email_template.get("subject"),
					'Body': {
						'ContentType': email_template.get("response"),
						'Content': "This is a test email."
					},
					'ToRecipients': [
					{
						'EmailAddress': {
							'Address': recipient
						}
					}]
				},
			'SaveToSentItems': 'true'}
			r= requests.post(endpoint,headers={'Authorization': 'Bearer ' + result['access_token']}, json=email_msg)
			if r.ok:
				print('Sent email successfully')
			else:
				print(r.json())
	else:
		print(result.get("error"))
		print(result.get("error_description"))
		print(result.get("correlation_id"))















# called from hooks on doc_event Email Unsubscribe
def unsubscribe_recipient(unsubscribe, method):
	if unsubscribe.reference_doctype == "Novacept Email Post":
		frappe.db.set_value("Novacept Email Post", unsubscribe.reference_name, "status", "Unsubscribed")


# called through hooks to update email campaign status daily
def set_email_campaign_status():
	email_post = frappe.get_all("Novacept Email Post", filters={"status": ("!=", "Unsubscribed")})
	for entry in email_post:
		email_camp = frappe.get_doc("Novacept Email Post", entry.name)
		email_camp.update_status()
