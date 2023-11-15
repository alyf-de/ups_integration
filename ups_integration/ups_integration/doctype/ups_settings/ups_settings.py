# Copyright (c) 2023, ALYF GmbH and contributors
# For license information, please see license.txt

import datetime

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime

API_BASE_URL = {
	"Customer Integration Environment": "https://wwwcie.ups.com",
	"Production Environment": "https://onlinetools.ups.com",
}


class UPSSettings(Document):
	def get_api_base_url(self) -> str:
		return API_BASE_URL.get(self.target_server, "")

	def get_bearer_token(self) -> str:
		try:
			access_token = self.get_password("access_token")
			if (
				access_token
				and self.expires
				and get_datetime(self.expires) > now_datetime() + datetime.timedelta(minutes=10)
			):
				return access_token
			else:
				return None
		except frappe.AuthenticationError:
			return None

	def get_client_id(self) -> str:
		return self.client_id

	def get_client_secret(self) -> str:
		try:
			return self.get_password("client_secret")
		except frappe.AuthenticationError:
			frappe.log_error(
				"Failed to retrieve Client-Secret from UPS Settings",
				reference_doctype="UPS Settings",
			)
			return None

	def set_access_token(self, access_token, issued_at, expires_in):
		self.access_token = access_token
		self.expires = datetime.datetime.fromtimestamp(int(issued_at) / 1000) + datetime.timedelta(
			seconds=int(expires_in)
		)
		self.save(ignore_permissions=True)
