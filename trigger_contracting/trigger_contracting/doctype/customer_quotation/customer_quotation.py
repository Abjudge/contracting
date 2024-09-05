# Copyright (c) 2024, TS and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CustomerQuotation(Document):
	def validate(self):
		calculate_total(self)



def calculate_total(self):
	sub_total = 0
	for item in self.items:
		if item.is_main:
			sub_total += item.amount
	self.sub_total = sub_total
	self.advance_payment_amount = self.sub_total * self.advance_payment_percentage / 100
	self.first_retention_amount = self.sub_total * self.first_retention_percentage / 100
	self.final_retention_amount = self.sub_total * self.final_retention_percentage / 100
	self.value_added_tax_amount = self.sub_total * self.value_added_tax_percentage / 100
	self.tax_deduction_and_addition_amount = self.sub_total * self.tax_deduction_and_addition_percentage / 100
	self.grand_total = self.sub_total + self.value_added_tax_amount - self.tax_deduction_and_addition_amount
