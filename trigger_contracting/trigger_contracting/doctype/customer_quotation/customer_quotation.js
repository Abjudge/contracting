// Copyright (c) 2024, TS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer Quotation", {
	refresh(frm) {
        if (frm.doc.docstatus == 1) { 
            frm.add_custom_button('Create Customer Contract', function() {
                create_customer_contract(frm)
            });
        }
	},
});

function create_customer_contract(frm){
	frappe.model.with_doctype('Customer Contract', function() {
		var customer_contract= frappe.model.get_new_doc('Customer Contract');
		
		customer_contract.project = frm.doc.project
        customer_contract.cost_center = frm.doc.cost_center
		customer_contract.customer = frm.doc.customer
		customer_contract.company = frm.doc.company
		customer_contract.transaction_date = frm.doc.transaction_date
		customer_contract.customer_quotation = frm.doc.name
		customer_contract.terms_and_condition = frm.doc.terms_and_condition
		customer_contract.custom_tender_number = frm.doc.custom_tender_number
		customer_contract.sub_total = frm.doc.sub_total
		customer_contract.advance_payment_percentage = frm.doc.advance_payment_percentage
		customer_contract.first_retention_percentage = frm.doc.first_retention_percentage
		customer_contract.final_retention_percentage = frm.doc.final_retention_percentage
		customer_contract.value_added_tax_percentage = frm.doc.value_added_tax_percentage
		customer_contract.tax_deduction_and_addition_percentage = frm.doc.tax_deduction_and_addition_percentage
		customer_contract.advance_payment_amount = frm.doc.advance_payment_amount
		customer_contract.first_retention_amount = frm.doc.first_retention_amount
		customer_contract.final_retention_amount = frm.doc.final_retention_amount
		customer_contract.value_added_tax_amount = frm.doc.value_added_tax_amount
		customer_contract.tax_deduction_and_addition_amount = frm.doc.tax_deduction_and_addition_amount

		frm.doc.items.forEach(function(item) {
			var customer_contract_item=frappe.model.add_child(customer_contract, 'items');
			customer_contract_item.business_item = item.business_item
			customer_contract_item.amount = item.amount
			customer_contract_item.is_main = item.is_main
			customer_contract_item.description = item.description
			customer_contract_item.number = item.number
			customer_contract_item.uom = item.uom
			customer_contract_item.contract_quantity = item.quantity
			customer_contract_item.rate = item.rate
			customer_contract_item.amount = item.amount
			// customer_contract_item.selling_price = item.selling_price
            customer_contract_item.project = frm.doc.project
            customer_contract_item.cost_center = frm.doc.cost_center
            customer_contract_item.business_item_name = frm.doc.business_item_name
		})

		frappe.set_route('Form', 'Customer Contract', customer_contract.name);
	
	})

}