# Copyright (c) 2024, TS and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


class SubcontractorsClearence(Document):
    def validate(self):
        if self.docstatus == 0:
            calculate_total(self)
            

    def on_submit(self):
        contract_doc = frappe.get_doc("Subcontractor Contract", self.subcontractor_contract)
        for item in self.items:
            for contract_item in contract_doc.items:
                if item.subcontractor_contract_item_row == contract_item.name:
                    contract_item.completed_quantity = item.total_qty
        contract_doc.on_update_after_submit()
        contract_doc.save()

    def on_cancel(self):
        contract_doc = frappe.get_doc("Subcontractor Contract", self.subcontractor_contract)
        for item in self.items:
            for contract_item in contract_doc.items:
                if item.subcontractor_contract_item_row == contract_item.name:
                    contract_item.completed_quantity = item.previous_qty
        contract_doc.on_update_after_submit()
        contract_doc.save()

def calculate_total(self):
	self.main_item_summary = []
	sub_total = 0
	for item in self.items:
		qty,amount = get_previous_clearance(self,item.subcontractor_contract_item_row)
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
				"business_item_name":item.business_item_name,
				"clearance_amount": item.current_amount,
				"contract_amount":item.contract_amount,
				"percentage":(item.current_amount / item.contract_amount) * 100
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




def get_previous_clearance(self,subcontractor_contract_item_row):
	qty,amount=0,0
	qty,amount = frappe.db.sql(f"""select sum(`tabS-Clearence Item`.current_qty) as 'qty',sum(`tabS-Clearence Item`.current_amount) as 'amount' from `tabS-Clearence Item` 
							inner join `tabSubcontractors Clearence` on `tabS-Clearence Item`.parent = `tabSubcontractors Clearence`.name 
							where `tabSubcontractors Clearence`.subcontractor_contract = '{self.subcontractor_contract}' and `tabSubcontractors Clearence`.docstatus = 1 and `tabSubcontractors Clearence`.name != '{self.name}'
							and `tabS-Clearence Item`.subcontractor_contract_item_row = '{subcontractor_contract_item_row}' """)[0]
	
	return qty,amount
@frappe.whitelist()
def create_journal_entry(doc):
    doc = json.loads(doc)
    
    setup_doc = frappe.get_doc("Subcontractors Setup", {"company": doc["company"]})
    
    advance_payment_account = setup_doc.advance_payment_account
    advance_payment_amount = round(doc.get("advance_payment_amount", 0), 2)

    first_retention_percentage_account = setup_doc.first_retention_percentage_account
    first_retention_amount = round(doc.get("first_retention_amount", 0), 2)

    final_retention_percentage_account = setup_doc.final_retention_percentage_account
    final_retention_amount = round(doc.get("final_retention_amount", 0), 2)

    tax_deduction_and_addition_account = setup_doc.tax_deduction_and_addition_account
    tax_deduction_and_addition_amount = round(doc.get("tax_deduction_and_addition_amount", 0), 2)

    deductions = []
    total_deductions = 0
    if "deductions" in doc:
        for deduction in doc["deductions"]:
            Deduction_Item_doc = frappe.get_doc("Deduction Item", deduction["deduction_name"])
            for row in Deduction_Item_doc.deduction_item_accounts:
                if row.company == doc["company"]:
                    amount = round(deduction["amount"], 2)
                    if amount != 0:
                        deductions.append({
                            "account": row.account,
                            "amount": amount
                        })
                        total_deductions += amount

    additions = []
    total_additions = 0
    if "additions" in doc:
        for addition in doc["additions"]:
            Addition_Item_doc = frappe.get_doc("Addition Item", addition["addition_name"])
            for row in Addition_Item_doc.addition_item_accounts:
                if row.company == doc["company"]:
                    amount = round(addition["amount"], 2)
                    if amount != 0:
                        additions.append({
                            "account": row.account,
                            "amount": amount
                        })
                        total_additions += amount

    subcontractors_account = setup_doc.subcontractors_account
    sub_total = round(doc.get("sub_total", 0), 2)
    
    value_added_tax_account = setup_doc.value_added_tax_account
    value_added_tax_amount = round(doc.get("value_added_tax_amount", 0), 2)

    total_credit_in_account_currency = (
        advance_payment_amount + 
        first_retention_amount + 
        final_retention_amount + 
        tax_deduction_and_addition_amount + 
        total_deductions + 
        total_additions
    )

    total_debit_in_account_currency = sub_total + value_added_tax_amount 

    amount_for_suppliers = abs(total_credit_in_account_currency - total_debit_in_account_currency)

    supplier_doc = frappe.get_doc("Supplier", doc["contractor"])
    supplier_account = ""
    for account in supplier_doc.accounts:
        if account.company == doc["company"]:
            supplier_account = account.account

    # Create the Journal Entry
    je = frappe.get_doc({
        "doctype": "Journal Entry",
        "posting_date": frappe.utils.nowdate(),
        'custom_subcontractors_clearence' : doc["name"],
        "company": doc["company"],
        "accounts": []
    })

    # Append non-zero accounts to the journal entry
    if sub_total != 0:
        je.append("accounts", {
            "account": subcontractors_account,
            "debit_in_account_currency": round(sub_total, 2),
            "credit_in_account_currency": 0,
            'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    if value_added_tax_amount != 0:
        je.append("accounts", {
            "account": value_added_tax_account,
            "debit_in_account_currency": round(value_added_tax_amount, 2),
            "credit_in_account_currency": 0,
            'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    if advance_payment_amount != 0:
        je.append("accounts", {
            "account": advance_payment_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": round(advance_payment_amount, 2),
            "party_type": "Supplier",
            "party": doc["contractor"],
            'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    if first_retention_amount != 0:
        je.append("accounts", {
            "account": first_retention_percentage_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": round(first_retention_amount, 2),
            "party_type": "Supplier",
            "party": doc["contractor"],
            'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    if final_retention_amount != 0:
        je.append("accounts", {
            "account": final_retention_percentage_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": round(final_retention_amount, 2),
            "party_type": "Supplier",
            "party": doc["contractor"],
            'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    if tax_deduction_and_addition_amount != 0:
        je.append("accounts", {
            "account": tax_deduction_and_addition_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": round(tax_deduction_and_addition_amount, 2),
            'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    if amount_for_suppliers != 0:
        je.append("accounts", {
            "account": supplier_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": round(amount_for_suppliers, 2),
            "party_type": "Supplier",
            "party": doc["contractor"],
            'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    # Handle deductions
    if deductions:
        for deduction in deductions:
            if "account" in deduction and "amount" in deduction and deduction["amount"] != 0:
                je.append("accounts", {
                    "account": deduction["account"],
                    "debit_in_account_currency": 0,
                    "credit_in_account_currency": round(deduction["amount"], 2),
                    'project': doc.get('project'),
                    'cost_center': doc.get('cost_center')
                })

    # Handle additions
    if additions:
        for addition in additions:
            if "account" in addition and "amount" in addition and addition["amount"] != 0:
                je.append("accounts", {
                    "account": addition["account"],
                    "debit_in_account_currency": 0,
                    "credit_in_account_currency": round(addition["amount"], 2),
                    "party_type": "Supplier",
                    "party": doc["contractor"],
                     'project': doc.get('project'),
                        'cost_center': doc.get('cost_center')
                })

    je.save()
    je.submit()
    frappe.msgprint("Journal Entry Created Successfully", title="Success", alert=True)

# def get_stamps(self):
# 	revenu_doc = frappe.get_doc("Revenue Setup",{
# 		"company":self.company
# 	})
# 	stamps = revenu_doc.stamps
# 	for stamp in stamps:
# 		self.append("stamps", {
# 			"stamp": stamp.stamp,
# 			"account": stamp.account,
# 			"percentage": stamp.percentage
# 		})

# def calc_amount_for_stamps(self):
# 	for stamp in self.stamps:
# 		stamp.amount = self.sub_total * stamp.percentage / 100
