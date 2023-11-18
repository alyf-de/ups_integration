# Copyright (c) 2023, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from ups_integration.ups_client import UPSClient

REQUEST_OPTIONS = {
	"Postal Code, State Province Code, City": "validate",
	"Postal Code, State Province Code": "nonvalidate",
}

SERVICES = {
	"Next Day Air": "01",
	"2nd Day Air": "02",
	"Ground": "03",
	"Express": "07",
	"Expedited": "08",
	"UPS Standard": "11",
	"3 Day Select": "12",
	"Next Day Air Saver": "13",
	"UPS Next Day Air Early": "14",
	"UPS Worldwide Economy DDU": "17",
	"Express Plus": "54",
	"2nd Day Air A.M.": "59",
	"UPS Saver": "65",
	"First Class Mail": "M2",
	"Priority Mail": "M3",
	"Expedited Mail Innovations": "M4",
	"Priority Mail Innovations": "M5",
	"Economy Mail Innovations": "M6",
	"Mail Innovations (MI) Returns": "M7",
	"UPS Access Point Economy": "70",
	"UPS Worldwide Express Freight Midday": "71",
	"UPS Worldwide Economy DDP": "72",
	"UPS Express 12:00": "74",
	"UPS Heavy Goods": "75",
	"UPS Today Standard": "82",
	"UPS Today Dedicated Courier": "83",
	"UPS Today Intercity": "84",
	"UPS Today Express": "85",
	"UPS Today Express Saver": "86",
	"UPS Worldwide Express Freight": "96",
}

PACKAGE_TYPES = {
	"UPS Letter": "01",
	"Customer Supplied Package": "02",
	"Tube": "03",
	"PAK": "04",
	"UPS Express Box": "21",
	"UPS 25KG Box": "24",
	"UPS 10KG Box": "25",
	"Pallet": "30",
	"Small Express Box": "2a",
	"Medium Express Box": "2b",
	"Large Express Box": "2c",
	"Flats": "56",
	"Parcels": "57",
	"BPM": "58",
	"First Class": "59",
	"Priority": "60",
	"Machineables": "61",
	"Irregulars": "62",
	"Parcel Post": "63",
	"BPM Parcel": "64",
	"Media Mail": "65",
	"BPM Flat": "66",
	"Standard Flat": "67",
}

CHARGE_TYPES = {
	"Transportation": "01",
	"Duties and Taxes": "02",
	"Broker of Choice": "03",
}

WEIGHT_UOMS = {
	"Pounds": "LBS",
	"Kilograms": "KGS",
	"Ounces": "OZS",
}


class UPSShipment(Document):
	def validate(self):
		# FIXME: Change to on_submit
		with UPSClient() as client:
			self.response = client.ship(self.get_shipment_request(), self.name)

	def get_shipment_request(self):
		shipment_request = {
			"Request": self.get_request(),
			"Shipment": self.get_shipment(),
		}

		if False:
			shipment_request["LabelSpecification"] = self.get_label_specification()

		if False:
			shipment_request["ReceiptSpecification"] = self.get_receipt_specification()

		return {"ShipmentRequest": shipment_request}

	def get_request(self):
		return {
			"SubVersion": frappe.db.get_single_value("UPS Settings", "api_version"),
			"RequestOption": REQUEST_OPTIONS.get(self.address_validation),
		}

	def get_shipment(self):
		shipment = {
			"Shipper": self.get_shipper(),
			"ShipTo": self.get_ship_to(),
			"PaymentInformation": self.get_payment_information(),
			"Service": self.get_service(),
			"Package": self.get_package(),
		}

		if self.description:
			shipment["Description"] = self.description

		return shipment

	def get_shipper(self):
		shipper = {
			"Name": self.shipper,
			"ShipperNumber": frappe.db.get_single_value("UPS Settings", "account_number"),
			"Address": self.get_shipper_address(),
		}

		return shipper

	def get_ship_to(self):
		ship_to = {
			"Name": self.ship_to,
			"Address": self.get_ship_to_address(),
		}

		return ship_to

	def get_payment_information(self):
		return {
			"ShipmentCharge": self.get_shipment_charge(),
		}

	def get_shipment_charge(self):
		shipment_charge = []

		for charge_item in self.charges:
			shipment_charge.append(
				{
					"Type": CHARGE_TYPES.get(charge_item.charge_type),
					"BillShipper": {
						"AccountNumber": frappe.db.get_single_value("UPS Settings", "account_number")
					},
				}
			)

		return shipment_charge

	def get_service(self):
		return {
			"Code": SERVICES.get(self.service),
		}

	def get_package(self):
		package = []

		for package_item in self.packages:
			package.append(
				{
					"Packaging": {"Code": PACKAGE_TYPES.get(package_item.package_type)},
					"PackageWeight": {
						"UnitOfMeasurement": {"Code": WEIGHT_UOMS.get(package_item.weight_uom)},
						"Weight": f"{package_item.weight}",
					},
				}
			)

		return package

	def get_ship_to_address(self):
		return self.get_address(self.ship_to_address)

	def get_shipper_address(self):
		return self.get_address(self.shipper_address)

	def get_address(self, address):
		address_doc = frappe.get_doc("Address", address)

		result = {
			"AddressLine": [
				line for line in [address_doc.address_line1, address_doc.address_line2] if line
			],
			"City": address_doc.city,
			"CountryCode": frappe.db.get_value("Country", address_doc.country, "code").upper(),
		}

		if address_doc.pincode:
			result["PostalCode"] = address_doc.pincode

		return result

	def get_label_specification(self):
		pass

	def get_receipt_specification(self):
		pass
