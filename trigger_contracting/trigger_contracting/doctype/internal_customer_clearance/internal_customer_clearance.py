# Copyright (c) 2024, TS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InternalCustomerClearance(Document):
		
	def validate(self):
		if self.is_new():
			doc = frappe.get_doc("Customer Contract", self.customer_contract)
			doc.append("customer_contract_refrances",{
				"internal_customer_clearance":self.name
			})
			doc.save()
		calculate_total(self)
		calc_amount_for_stamps(self)

def calculate_total(self):
	self.main_item_summary = []
	sub_total = 0
	for item in self.items:
		qty,amount = get_previous_clearance(self,item.customer_contract_item_row)
		item.previous_qty = qty if qty else 0
		item.previous_amount = amount if amount else 0
		item.previouse_percentage = ((amount if amount else 0) / item.contract_amount) * 100
		item.current_percentage = ((item.current_amount if item.current_amount else 0)/ (item.contract_amount if item.contract_amount else 0)) * 100
		# calc current
		item.current_qty = (item.current_qty if item.current_qty else 0)
		item.current_amount = (item.current_qty if item.current_qty else 0) * (item.contract_rate if item.current_qty else 0)
		item.current_percentage = (item.current_amount / item.contract_amount) * 100
		# calc Totals
		item.total_qty = (item.current_qty if item.current_qty else 0) + (item.previous_qty if item.previous_qty else 0)
		item.total_amount = (item.current_amount if item.current_amount else 0) + (item.previous_amount if item.previous_amount else 0)
		item.total_percentage = (item.total_amount / item.contract_amount) * 100
	total_amount = 0
	current_amount = 0
	for item in reversed(self.items):
		if item.is_main:
			item.contract_qty = 0
			item.contract_rate = 0
			item.current_qty =0
			item.current_percentage = 0
			item.total_amount = total_amount
			item.current_amount = current_amount
			total_amount = 0
			current_amount = 0
		else:
			total_amount += item.total_amount
			current_amount += item.current_amount

	sub_total = 0
	for item in self.items:
		if item.is_main:
			sub_total += item.total_amount
			self.append("main_item_summary", {
				"main_item": item.business_item,
				"clearance_amount": item.current_amount,
				"contract_amount":item.contract_amount,
				"percentage":(item.current_amount / item.contract_amount) * 100,
				"business_item_name":item.business_item_name
			})

	self.sub_total = sub_total
	self.advance_payment_amount = self.sub_total * (self.advance_payment_percentage if self.advance_payment_percentage else 0 )/ 100
	self.first_retention_amount = self.sub_total * (self.first_retention_percentage if self.first_retention_percentage else 0) / 100
	self.final_retention_amount = self.sub_total * (self.final_retention_percentage if self.final_retention_percentage else 0) / 100
	self.value_added_tax_amount = self.sub_total * (self.value_added_tax_percentage if self.value_added_tax_percentage else 0) / 100
	self.tax_deduction_and_addition_amount = self.sub_total * (self.tax_deduction_and_addition_percentage if self.tax_deduction_and_addition_percentage else 0) / 100

	deductions = 0
	for d in self.deductions:
		deductions += d.amount
	self.total_deduction = deductions
	additions = 0
	for a in self.additions:
		additions += a.amount
	self.total_addition = additions

	self.grand_total = self.sub_total + self.value_added_tax_amount - self.advance_payment_amount - self.first_retention_amount - self.final_retention_amount - self.tax_deduction_and_addition_amount + additions - deductions




def get_previous_clearance(self,customer_contract_item_row):
	qty,amount=0,0
	qty,amount = frappe.db.sql(f"""select sum(`tabInternal Clearence Item`.current_qty) as 'qty',sum(`tabInternal Clearence Item`.current_amount) as 'amount' from `tabInternal Clearence Item` 
							inner join `tabInternal Customer Clearance` on `tabInternal Clearence Item`.parent = `tabInternal Customer Clearance`.name 
							where `tabInternal Customer Clearance`.customer_contract = '{self.customer_contract}' and `tabInternal Customer Clearance`.docstatus = 1 and `tabInternal Customer Clearance`.name != '{self.name}'
							and `tabInternal Clearence Item`.customer_contract_item_row = '{customer_contract_item_row}' """)[0]
	
	return qty,amount



def calc_amount_for_stamps(self):
	for stamp in self.stamps:
		stamp.amount = self.sub_total * stamp.percentage / 100