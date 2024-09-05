# Copyright (c) 2024, TS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BOQ(Document):
	def validate(self):
		if self.boq_item:
			calc_boq_item(self)
			self.total_material_cost=calc_tabls(self.boq_item)
		else:
			self.total_material_cost=0
		if self.labor_table:
			self.labor_cost=calc_tabls(self.labor_table)
		else:
			self.labor_cost=0
		if self.required_equipment:
			self.equipment_cost=calc_tabls(self.required_equipment)
		else:
			self.equipment_cost=0
		if self.subcontractors:
			self.total_subcontractors_cost=calc_tabls(self.subcontractors)
		else:
			self.total_subcontractors_cost=0
		if self.other_expenses:
			self.total_expenses_cost=calc_tabls(self.other_expenses)
		else:
			self.total_expenses_cost=0
	
		calc_grand_total(self)
		
		
	def on_submit(self):
		doc = frappe.get_doc("Costing Voucher", self.costing_voucher)
		for row in doc.costing_voucher_items:
			if self.c_v_row_id == row.name:
				row.direct_cost = self.grand_total/self.project__quantity
				row.boq_id = self.name

		doc.validate()
		doc.save()

	

  


def calc_grand_total(self):
	self.grand_total = 0
	totals=(
        (self.total_material_cost or 0) + 
        (self.labor_cost or 0) + 
        (self.equipment_cost or 0) + 
        (self.total_subcontractors_cost or 0) + 
        (self.total_expenses_cost or 0)
    )
	self.grand_total=totals

def calc_tabls(child_table):
	total_cost=0
	for item in child_table:
		total_cost += item.amount or 0
	return total_cost

def calc_boq_item(self):
	if len(self.boq_item) >0:
		for item in self.boq_item:
			item.rate = (self.project__quantity or 0 )* (item.unit_rate or 0)
			item.amount=(item.quantity or 0) * (item.rate or 0)



