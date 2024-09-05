# Copyright (c) 2024, TS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SubcontractorContract(Document):
    @frappe.whitelist()
    def create_payment(self, mode_of_payment):
        # Log some debug information

        if not self.advance_payment_amount or self.advance_payment_amount <= 0:
            frappe.throw("Received Amount (Advance Payment Amount) must be set and greater than zero.")

        # Create a new Payment Entry document
        payment_doc = frappe.get_doc({
            'doctype': 'Payment Entry',
            'custom_subcontractor_contract': self.name,
            'posting_date': frappe.utils.nowdate(),
            'company': self.company,
            'cost_center': self.cost_center,
			'project': self.project,
            'payment_type': 'Pay',
            'mode_of_payment': mode_of_payment,
            'party_type': 'Supplier',
            'party': self.contractor,
            'party_name': self.contractor_name,
            'paid_amount': self.advance_payment_amount,
            'received_amount': self.advance_payment_amount,
        })

        # Fetch the account paid from using mode of payment
        account_paid_from = frappe.db.get_value('Mode of Payment Account', 
            {'parent': mode_of_payment, 'company': self.company}, 
            'default_account')

        if account_paid_from:
            payment_doc.paid_from = account_paid_from
        else:
            frappe.throw(f"Could not find account for Mode of Payment: {mode_of_payment}")

        # Fetch the account paid to (supplier account)
        account_paid_to = frappe.db.get_value('Subcontractors Setup', 
            {'company': self.company}, 
            'advance_payment_account')

        if account_paid_to:
            payment_doc.paid_to = account_paid_to
        else:
            frappe.throw(f"Could not find account for Contractor: {self.contractor}")

        # Save and submit the payment entry
        payment_doc.insert()
        # payment_doc.submit()

        # Generate the link to the created Payment Entry
        payment_entry_url = frappe.utils.get_url_to_form('Payment Entry', payment_doc.name)

        # Return a success message with the link
        return frappe.msgprint(f"Payment Entry created successfully: <a href='{payment_entry_url}'>{payment_doc.name}</a>")

    def validate(self):
        calculate_total(self)
    
    def on_update_after_submit(self):
        if self.docstatus == 1:
            calculate_total_after_submit(self)

def calculate_total(self):
    self.main_item_summary = []
    sub_total = 0
    for item in self.items:
        item.max_allowed_qty = ((item.allowance_percentage if item.allowance_percentage else 0) / 100) * (item.contract_quantity if item.contract_quantity else 0) + (item.contract_quantity if item.contract_quantity else 0)
        item.max_allowed_amount = (item.max_allowed_qty if item.max_allowed_qty else 0) * (item.rate if item.rate else 0)
        item.remaining__quantity = (item.max_allowed_qty if item.max_allowed_qty else 0) - (item.completed_quantity if item.completed_quantity else 0)
        item.completed_amount = (item.completed_quantity if item.completed_quantity else 0) * (item.rate if item.rate else 0)
        amount, max_allowed_amount, completed_amount = 0, 0, 0
    
    for item in reversed(self.items):
        if item.is_main:
            item.amount = amount
            item.max_allowed_amount = max_allowed_amount
            item.completed_amount = completed_amount
            amount, max_allowed_amount, completed_amount = 0, 0, 0
        else:
            amount += (item.amount if item.amount else 0)
            max_allowed_amount += (item.max_allowed_amount if item.max_allowed_amount else 0)
            completed_amount += (item.completed_amount if item.completed_amount else 0)
    
    for item in self.items:
        if item.is_main:
            sub_total += item.amount
            self.append("main_item_summary", {
                "contract_amount": item.amount,
                "main_item": item.business_item,
                "business_item_name": item.business_item_name,
                "completed_amount": item.completed_amount,
                "percentage": item.completed_amount / item.amount * 100 if item.amount != 0 else 0
            })
    
    self.sub_total = sub_total
    self.advance_payment_amount = (self.sub_total or 0) * (self.advance_payment_percentage or 0) / 100
    self.first_retention_amount = (self.sub_total or 0) * (self.first_retention_percentage or 0) / 100
    self.final_retention_amount = (self.sub_total or 0) * (self.final_retention_percentage or 0) / 100
    self.value_added_tax_amount = (self.sub_total or 0) * (self.value_added_tax_percentage or 0) / 100
    self.tax_deduction_and_addition_amount = (self.sub_total or 0) * (self.tax_deduction_and_addition_percentage or 0) / 100
    self.grand_total = (self.sub_total or 0) + (self.value_added_tax_amount or 0) - (self.advance_payment_amount or 0) - (self.first_retention_amount or 0) - (self.final_retention_amount or 0) - (self.tax_deduction_and_addition_amount or 0)

def calculate_total_after_submit(self):
    for item in self.items:
        item.max_allowed_qty = (item.allowance_percentage / 100) * item.contract_quantity + item.contract_quantity
        item.max_allowed_amount = item.max_allowed_qty * item.rate 
        item.remaining__quantity = (item.max_allowed_qty if item.max_allowed_qty else 0) - (item.completed_quantity if item.completed_quantity else 0)
        item.completed_amount = (item.completed_quantity if item.completed_quantity else 0) * item.rate
        item.poc = (item.completed_amount / item.amount) * 100

    amount, max_allowed_amount, completed_amount = 0, 0, 0
    for item in reversed(self.items):
        if item.is_main:
            item.amount = amount
            item.max_allowed_amount = max_allowed_amount
            item.completed_amount = completed_amount
            item.poc = (item.completed_amount / item.amount) * 100
            amount, max_allowed_amount, completed_amount = 0, 0, 0
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
                "business_item_name": item.business_item_name,
                "completed_amount": item.completed_amount,
                "percentage": (item.completed_amount / item.max_allowed_amount) * 100
            })
