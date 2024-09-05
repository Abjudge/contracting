# Copyright (c) 2024, TS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CustomerContract(Document):
	def validate(self):
		if not self.stamps:
			get_stamps(self)
		if self.docstatus != 1:
			calculate_total(self)
		if self.stamps and self.sub_total:
			calc_amount_for_stamps(self)

	def on_update_after_submit(self):
		if self.docstatus == 1:
			calculate_total_after_submit(self)
			create_customer_contract_versions(self)

def calculate_total(self):
	
	self.main_item_summary = []
	sub_total = 0
	for item in self.items:
		if not item.is_main:
			item.amount = item.contract_quantity * item.rate
			item.max_allowed_qty = ((item.allowance_percentage if item.allowance_percentage else 0) / 100) * (item.contract_quantity if item.contract_quantity else 0) + (item.contract_quantity if item.contract_quantity else 0)
			item.max_allowed_amount = item.max_allowed_qty * item.rate 
			item.remaining__quantity = (item.max_allowed_qty if item.max_allowed_qty else 0) - (item.completed_quantity if item.completed_quantity else 0)
			item.completed_amount = (item.completed_quantity if item.completed_quantity else 0 )* item.rate
			item.poc = (item.completed_amount / item.amount or 1) * 100
			amount,max_allowed_amount,completed_amount = 0,0,0
	for item in reversed(self.items):
		if item.is_main:
			item.amount = amount
			item.max_allowed_amount = max_allowed_amount
			item.completed_amount = completed_amount
			item.poc = (item.completed_amount / item.amount or 1) * 100
			amount,max_allowed_amount,completed_amount = 0,0,0
		else:
			amount += item.amount
			max_allowed_amount += (item.max_allowed_amount if item.max_allowed_amount else 0)
			completed_amount += (item.completed_amount if item.completed_amount else 0)
	for item in self.items:
		if item.is_main:
			sub_total += item.amount
			self.append("main_item_summary", {
				"contract_amount": item.amount,
				"main_item": item.business_item,
				"completed_amount": item.completed_amount,
				"percentage":item.completed_amount / item.amount * 100,
				"business_item_name":item.business_item_name
			})
	self.sub_total = sub_total
	self.advance_payment_amount = self.sub_total * self.advance_payment_percentage / 100
	self.first_retention_amount = self.sub_total * self.first_retention_percentage / 100
	self.final_retention_amount = self.sub_total * self.final_retention_percentage / 100
	self.value_added_tax_amount = self.sub_total * self.value_added_tax_percentage / 100
	self.tax_deduction_and_addition_amount = self.sub_total * self.tax_deduction_and_addition_percentage / 100
	self.grand_total = self.sub_total + self.value_added_tax_amount - self.advance_payment_amount - self.first_retention_amount - self.final_retention_amount - self.tax_deduction_and_addition_amount




def calculate_total_after_submit(self):
	for item in self.items:
		item.amount = item.contract_quantity * item.rate
		item.max_allowed_qty = (item.allowance_percentage / 100) * item.contract_quantity + item.contract_quantity
		item.max_allowed_amount = item.max_allowed_qty * item.rate 
		item.remaining__quantity = (item.max_allowed_qty if item.max_allowed_qty else 0) - (item.completed_quantity if item.completed_quantity else 0)
		item.completed_amount = (item.completed_quantity if item.completed_quantity else 0 )* item.rate
		item.poc = (item.completed_amount / item.amount if item.amount > 0 else 1) * 100

	amount,max_allowed_amount,completed_amount = 0,0,0
	for item in reversed(self.items):
		if item.is_main:
			item.contract_quantity = 0
			item.rate = 0
			
			item.amount = amount
			item.max_allowed_amount = max_allowed_amount
			item.completed_amount = completed_amount
			item.poc = (item.completed_amount / item.amount) * 100
			amount,max_allowed_amount,completed_amount = 0,0,0
		else:
			amount += item.amount
			max_allowed_amount += item.max_allowed_amount
			completed_amount += item.completed_amount
	self.main_item_summary = []
	for item in self.items:
		if item.is_main:
			self.append("main_item_summary", {
				"contract_amount": item.max_allowed_amount,
				"main_item": item.business_item,
				"completed_amount": item.completed_amount,
				"percentage":(item.completed_amount / item.amount ) *100
			})
			

def create_customer_contract_versions(self):
	cc_doc = self.get_doc_before_save()
	if cc_doc:
		cc_doc = cc_doc.as_dict()
		ccv_doc = frappe.new_doc("Customer Contract Versions")
		ccv_doc.update(cc_doc)
		ccv_doc.customer_contract = self.name
		ccv_doc.save()
		ccv_doc.submit()

def get_stamps(self):
	revenu_doc = frappe.get_doc("Revenue Setup",{
		"company":self.company
	})
	stamps = revenu_doc.stamps
	for stamp in stamps:
		self.append("stamps", {
			"stamp": stamp.stamp,
			"account": stamp.account,
			"percentage": stamp.percentage
		})

def calc_amount_for_stamps(self):
	for stamp in self.stamps:
		stamp.amount = self.sub_total * stamp.percentage / 100
