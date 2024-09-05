# Copyright (c) 2024, TS and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


class CustomerClearence(Document):
    def validate(self):
        calculate_total(self)
        calc_amount_for_stamps(self)

    def on_submit(self):
        contract_doc = frappe.get_doc("Customer Contract", self.customer_contract)
        for item in self.items:
            for contract_item in contract_doc.items:
                if item.customer_contract_item_row == contract_item.name:
                    contract_item.completed_quantity = item.total_qty
        if self.internal_customer_clearance:
            if len(contract_doc.customer_contract_refrances) > 0:
                for i in contract_doc.customer_contract_refrances:
                    if i.internal_customer_clearance == self.internal_customer_clearance:
                        i.customer_clearence = self.name

        contract_doc.on_update_after_submit()
        contract_doc.save()

    def on_cancel(self):
        contract_doc = frappe.get_doc("Customer Contract", self.customer_contract)
        for item in self.items:
            for contract_item in contract_doc.items:
                if item.customer_contract_item_row == contract_item.name:
                    contract_item.completed_quantity = item.previous_qty
        if self.internal_customer_clearance:
            if len(contract_doc.customer_contract_refrances) > 0:
                for i in contract_doc.customer_contract_refrances:
                    if i.internal_customer_clearance == self.internal_customer_clearance:
                        i.customer_clearence = ""
        contract_doc.on_update_after_submit()
        contract_doc.save()




def calculate_total(self):
	self.main_item_summary = []
	sub_total = 0
	for item in self.items:
		qty,amount = get_previous_clearance(self,item.customer_contract_item_row)
		item.previous_qty = qty if qty else 0
		item.previous_amount = amount if amount else 0
		item.previouse_percentage = ((qty if qty else 0) / item.contract_qty if  item.contract_qty > 0 else 1) * 100
		item.current_percentage = ((item.current_amount if item.current_amount else 0)/ (item.contract_amount if item.contract_amount else 0)) * 100
		# calc current
		item.current_qty = (item.current_qty if item.current_qty else 0)
		# item.current_amount = (item.current_qty or 0) * (item.contract_rate or 0) * (item.rate or 0)/100
		item.current_amount = (item.current_qty or 0)  * (item.rate or 0)
		item.current_percentage = (item.current_qty / item.contract_qty if  item.contract_qty > 0 else 1) * 100
		# calc Totals
		item.total_qty = (item.current_qty if item.current_qty else 0) + (item.previous_qty if item.previous_qty else 0)
		item.total_amount = (item.current_amount if item.current_amount else 0) + (item.previous_amount if item.previous_amount else 0)
		item.total_percentage = (item.total_qty / item.contract_qty if  item.contract_qty > 0 else 1) * 100
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
	qty,amount = frappe.db.sql(f"""select sum(`tabClearence Item`.current_qty) as 'qty',sum(`tabClearence Item`.current_amount) as 'amount' from `tabClearence Item` 
							inner join `tabCustomer Clearence` on `tabClearence Item`.parent = `tabCustomer Clearence`.name 
							where `tabCustomer Clearence`.customer_contract = '{self.customer_contract}' and `tabCustomer Clearence`.docstatus = 1 and `tabCustomer Clearence`.name != '{self.name}'
							and `tabClearence Item`.customer_contract_item_row = '{customer_contract_item_row}' """)[0]
	
	return qty,amount


@frappe.whitelist()
def create_journal_entry(doc):
    doc = json.loads(doc)
    
    setup_doc = frappe.get_doc("Revenue Setup", {"company": doc["company"]})
    
    # debit account and amounts
    advance_payment_account = setup_doc.advance_payment_account
    advance_payment_amount = round(doc.get("advance_payment_amount", 0), 2)

    first_retention_percentage_account = setup_doc.business_insurance_account
    first_retention_amount = round(doc.get("first_retention_amount", 0), 2)

    final_retention_percentage_account = setup_doc.final_retention_account
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

    stamps = []
    total_stamps = 0
    if "stamps" in doc:
        for stamp in doc["stamps"]:
            amount = round(stamp["amount"], 2)
            account = stamp["account"]
            if amount != 0:
                stamps.append({
                    "account": account,
                    "amount": amount
                })
                total_stamps += amount

    # Credit accounts and amounts
    accrual_revenue_account = setup_doc.accrual_revenue_account
    sub_total = round(doc.get("sub_total", 0), 2)
    
    value_added_tax_account = setup_doc.value_added_tax_account
    value_added_tax_amount = round(doc.get("value_added_tax_amount", 0), 2)

    total_debit_in_account_currency = (
        advance_payment_amount + 
        first_retention_amount + 
        final_retention_amount + 
        tax_deduction_and_addition_amount + 
        total_deductions + 
        total_additions +
        total_stamps
    )

    total_credit_in_account_currency = sub_total + value_added_tax_amount 

    amount_for_customer = abs(total_credit_in_account_currency - total_debit_in_account_currency)

    customer_doc = frappe.get_doc("Customer", doc["customer"])
    customer_account = ""
    for account in customer_doc.accounts:
        if account.company == doc["company"]:
            customer_account = account.account

    # Create the Journal Entry
    je = frappe.get_doc({
        "doctype": "Journal Entry",
        "posting_date": frappe.utils.nowdate(),
        "company": doc["company"],
        'custom_customer_clearence' : doc["name"],
        "accounts": []
    })

    if amount_for_customer != 0:
        je.append("accounts", {
            "account": customer_account,
            "debit_in_account_currency": round(amount_for_customer, 2),
            "credit_in_account_currency": 0,
            "party_type": "Customer",
            "party": doc["customer"],
            'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    if advance_payment_amount != 0:
        je.append("accounts", {
            "account": advance_payment_account,
            "debit_in_account_currency": round(advance_payment_amount, 2),
            "credit_in_account_currency": 0,
            "party_type": "Customer",
            "party": doc["customer"],
            'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    if first_retention_amount != 0:
        je.append("accounts", {
            "account": first_retention_percentage_account,
            "debit_in_account_currency": round(first_retention_amount, 2),
            "credit_in_account_currency": 0,
            "party_type": "Customer",
            "party": doc["customer"],
            'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    if final_retention_amount != 0:
        je.append("accounts", {
            "account": final_retention_percentage_account,
            "debit_in_account_currency": round(final_retention_amount, 2),
            "credit_in_account_currency": 0,
            "party_type": "Customer",
            "party": doc["customer"],
            'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    if tax_deduction_and_addition_amount != 0:
        je.append("accounts", {
            "account": tax_deduction_and_addition_account,
            "debit_in_account_currency": round(tax_deduction_and_addition_amount, 2),
            "credit_in_account_currency": 0,
            'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    # Handle deductions
    if deductions:
        for deduction in deductions:
            if "account" in deduction and "amount" in deduction and deduction["amount"] != 0:
                je.append("accounts", {
                    "account": deduction["account"],
                    "debit_in_account_currency": round(deduction["amount"], 2),
                    "credit_in_account_currency": 0,
                    'project': doc.get('project'),
                    'cost_center': doc.get('cost_center')
                })

    # Handle additions
    if additions:
        for addition in additions:
            if "account" in addition and "amount" in addition and addition["amount"] != 0:
                je.append("accounts", {
                    "account": addition["account"],
                    "debit_in_account_currency": round(addition["amount"], 2),
                    "credit_in_account_currency": 0,
                    "party_type": "Customer",
                    "party": doc["customer"],
                    'project': doc.get('project'),
                    'cost_center': doc.get('cost_center')
                })

    if stamps:
        for stamp in stamps:
            if "account" in stamp and "amount" in stamp and stamp["amount"] != 0:
                je.append("accounts", {
                    "account": stamp["account"],
                    "debit_in_account_currency": round(stamp["amount"], 2),
                    "credit_in_account_currency": 0,
                    'project': doc.get('project'),
                    'cost_center': doc.get('cost_center')
                })

    if sub_total != 0:
        je.append("accounts", {
            "account": accrual_revenue_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": round(sub_total, 2),
             'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    if value_added_tax_amount != 0:
        je.append("accounts", {
            "account": value_added_tax_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": round(value_added_tax_amount, 2),
            'project': doc.get('project'),
            'cost_center': doc.get('cost_center')
        })

    je.save()
    je.submit()
    frappe.msgprint("Journal Entry Created Successfully", title="Success", alert=True)

def calc_amount_for_stamps(self):
	for stamp in self.stamps:
		stamp.amount = self.sub_total * stamp.percentage / 100