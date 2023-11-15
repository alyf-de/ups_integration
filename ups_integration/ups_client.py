# Copyright (c) 2023, ALYF GmbH and Contributors
# See license.txt

import frappe
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout


class UPSClient:
	def __init__(self):
		self.api_base_url = self.get_api_base_url()
		self.session = None

	def __enter__(self):
		self.session = self._create_session()
		self.bearer_token = self._get_or_create_token()
		self._set_authorization_header()

		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self._close_session()

	def _create_session(self):
		session = requests.Session()
		session.mount(self.api_base_url, HTTPAdapter(max_retries=3))

		return session

	def _get_or_create_token(self):
		token = frappe.get_single("UPS Settings").get_bearer_token()

		return token or self._create_token()

	def _set_authorization_header(self):
		self.session.headers.update({"Authorization": f"Bearer {self.bearer_token}"})

	def _close_session(self):
		if self.session:
			self.session.close()

	def _create_token(self):
		url = f"{self.api_base_url}/security/v1/oauth/token"
		payload = {"grant_type": "client_credentials"}
		headers = {
			"Content-Type": "application/x-www-form-urlencoded",
			"x-merchant-id": "erpnext-h38dj3",
		}

		auth = self._get_auth_credentials()
		token_response = self.request("POST", url, data=payload, headers=headers, auth=auth)

		if token_response:
			token_data = token_response.json()
			self._save_access_token(token_data)

			return token_data.get("access_token")

	def _get_auth_credentials(self):
		ups_settings = frappe.get_single("UPS Settings")

		return ups_settings.get_client_id(), ups_settings.get_client_secret()

	def _save_access_token(self, token_data):
		frappe.get_single("UPS Settings").set_access_token(
			token_data.get("access_token"),
			token_data.get("issued_at"),
			token_data.get("expires_in"),
		)

	def get_api_base_url(self):
		return frappe.get_single("UPS Settings").get_api_base_url()

	def request(self, method, url, **kwargs):
		try:
			response = self.session.request(method, url, **kwargs)
			response.raise_for_status()

			return response
		except HTTPError as e:
			frappe.log_error("UPS API Request HTTP Error", e)
		except ConnectionError as e:
			frappe.log_error("UPS API Request Connection Error", e)
		except Timeout as e:
			frappe.log_error("UPS API Request Timeout Error", e)
		except RequestException as e:
			frappe.log_error("UPS API Request General Error", e)
		except Exception as e:
			frappe.log_error("UPS API Request Unexpected Error", e)

		return None
