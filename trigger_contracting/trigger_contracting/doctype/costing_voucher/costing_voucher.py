# Copyright (c) 2024, TS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CostingVoucher(Document):
    def on_submit(self):
        for row in self.costing_voucher_items:
            frappe.db.set_value("Project Items", row.project_row_id, {
                'rate':row.selling_rate,
                'amount':row.selling_amount,
                'quantity':row.quantity,
                # 'selling_price':row.selling_amount
            })
        project_doc = frappe.get_doc("Project", self.project)
        project_doc.project_items_summary = []
        for row in self.costing_voucher_main_business_items:
            project_doc.append("project_items_summary", {
                "main_item":row.main_business_item,
                "contract_amount":row.selling_price,
            })
        project_doc.save()
        Project_Req_Material_doc=frappe.new_doc("Project Required Material")
        Project_Req_Material_doc.costing_voucher=self.name
        Project_Req_Material_doc.project=self.project
        Project_Req_Material_doc.transaction_date=self.date

        items_dict = {}  # Dictionary to store item quantities, rates, and amounts

        for item in self.costing_voucher_items:
            if item.is_main == 0:
                doc = frappe.get_doc("BOQ", item.boq_id)
                for child_table in doc.boq_item:
                    item_group = child_table.item_group
                    quantity = child_table.quantity
                    rate = child_table.rate
                    amount = child_table.amount

                    # Update the quantity, rate, and amount in the dictionary
                    if item_group in items_dict:
                        items_dict[item_group]["quantity"] += quantity
                        items_dict[item_group]["rate"] += rate
                        items_dict[item_group]["amount"] += amount
                    else:
                        items_dict[item_group] = {"quantity": quantity, "rate": rate, "amount": amount}

        # Add the items to the Project Required Material document
        for item_group, item_data in items_dict.items():
            Project_Req_Material_doc.append("items", {
                'item_group': item_group,
                'quantity': item_data["quantity"],
                'remaining_quantity': item_data["quantity"],
                'rate': item_data["rate"],
                'amount': item_data["amount"]
            })

        Project_Req_Material_doc.save()
        Project_Req_Material_doc.submit()


    def validate(self):
        calc_costing_voucher_direct_cost(self)
        calc_costing_voucher_indirect_cost(self)
        clac_costing_voucher_markup_cost(self)
        calc_margin(self)
        calc_indirect_markup_cost(self)


def calc_costing_voucher_direct_cost(self):
    if len(self.costing_voucher_items) > 0:
        total_direct_cost = 0
        for row in self.costing_voucher_items:
            total_direct_cost += row.direct_cost or 0
        self.total_direct_cost = total_direct_cost

def calc_costing_voucher_indirect_cost(self):
    if len(self.costing_voucher_indirect_cost) > 0:
        total_indirect_cost = 0
        for row in self.costing_voucher_indirect_cost:
            total_indirect_cost += row.amount
        self.total_indirect_cost = total_indirect_cost

def clac_costing_voucher_markup_cost(self):
    if len(self.costing_voucher_markup_cost) > 0:
        total_markup_cost = 0
        for row in self.costing_voucher_markup_cost:
            total_markup_cost += row.amount
        self.total_markup_cost = total_markup_cost


def calc_margin(self):
    if self.total_direct_cost > 0:
        self.margin = (self.total_direct_cost + self.total_indirect_cost + self.total_markup_cost) / self.total_direct_cost
    else:
        self.margin = 0
    if len(self.costing_voucher_items) > 0:
        for row in self.costing_voucher_items:
            if row.is_main != 1:
                row.margin = self.margin

def calc_indirect_markup_cost(self):
    if len(self.costing_voucher_items) > 0:
        one_cost_indirect_cost,one_cost_markup_cost = 0,0
        if self.total_direct_cost > 0:
            one_cost_indirect_cost = self.total_indirect_cost / self.total_direct_cost
            one_cost_markup_cost = self.total_markup_cost / self.total_direct_cost
        amount = 0
        for row in self.costing_voucher_items:
            if row.is_main != 1:  
                row.indirect_cost = one_cost_indirect_cost 
                row.markup_cost = one_cost_markup_cost 

                row.rate = (row.direct_cost or 0) + (row.indirect_cost or 0) + (row.markup_cost or 0)
                row.amount = row.rate * row.quantity
                amount += row.amount
                row.selling_amount = row.amount * (1+(row.margin/100))
                row.selling_rate=row.selling_amount/row.quantity if row.quantity > 0 else 1
        self.total = amount
        amount  = 0
        selling_amount = 0
        total_selling_amount = 0
        
        for row in reversed(self.costing_voucher_items):
            
            if row.is_main == 0:
                amount += row.amount
                selling_amount += row.selling_amount
                total_selling_amount += row.selling_amount
                
            else:
                row.amount = amount
                row.selling_amount = selling_amount
                amount = 0
                selling_amount = 0
        self.costing_voucher_main_business_items = []
        for row in self.costing_voucher_items:
            if row.is_main == 1:
                self.append("costing_voucher_main_business_items", {
                "main_business_item":row.business_item,
                "cost":row.amount,
                "selling_price":row.selling_amount,
                "profit":(row.selling_amount - row.amount) ,
                "profit_percentage":((row.selling_amount - row.amount)/ (row.selling_amount if row.selling_amount > 0 else 1)) * 100
                })
        self.total_cost_before_tax = total_selling_amount
        self.tax_amount = total_selling_amount * ((self.tax_percentage or 0)/100)
        self.total_cost_with_tax = self.total_cost_before_tax + self.tax_amount

        
            
                
