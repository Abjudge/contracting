// Copyright (c) 2024, TS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Subcontractor Contract", {

    subcontractors_setup(frm){
        if(frm.doc.subcontractors_setup){
            frappe.db.get_doc("Subcontractors Setup",frm.doc.subcontractors_setup).then(doc => {
                console.log(doc)
                frm.set_value("advance_payment_percentage", doc.advance_payment__percentage)
                frm.set_value("first_retention_percentage", doc.first_retention_percentage)
                frm.set_value("final_retention_percentage", doc.final_retention_percentage)
                frm.set_value("value_added_tax_percentage", doc.value_added_tax_percentage)
                frm.set_value("tax_deduction_and_addition_percentage", doc.tax_deduction_and_addition__percentage)
            })
        }
        else{
            frm.set_value("advance_payment_percentage", 0)
            frm.set_value("first_retention_percentage", 0)
            frm.set_value("final_retention_percentage", 0)
            frm.set_value("value_added_tax_percentage", 0)
            frm.set_value("tax_deduction_and_addition_percentage", 0)
        }
       
    },
	refresh(frm) {
        if (frm.doc.docstatus == 1) { 
            frm.add_custom_button('Create Subcontractor Clearance', function() {
                create_subcontractor_clearence(frm)
            });
            frm.add_custom_button('Create payment Entry', function() {
                create_payment(frm)
            });
        }

        frm.fields_dict['cost_center'].get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    "company": doc.company // Filter based on the selected company
                }
            };
        };
        frm.fields_dict['business_item'].get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    "project": doc.project // Filter based on the selected company
                }
            };
        };

	},
    setup(frm) {
        frm.set_query('related_business_item', 'items', function(doc, cdt, cdn) {
            return {
                filters: {
                    'project': frm.doc.project
                    
                }
            };
        });
    },
    set_seriesline(frm){
		var index = 0
		var subindex = 1
        for(let i=0;i<frm.doc.items.length ; i++){
            if(frm.doc.items[i].is_main == 1){
				    index +=1 
					subindex = 1
					frm.doc.items[i].number = index
            }
            else{
				frm.doc.items[i].number = index + "-" + subindex
				subindex = subindex +1
            }
        }
        frm.refresh_field("items")
    },
	calc_totals(frm){
		let sumAmount = 0;
		// Iterate over the data in reverse order
		for (let i = frm.doc.items.length - 1; i >= 0; i--) {
			// If is_main is 0, add the amount to the sum
			if (frm.doc.items[i].is_main === 0) {
				sumAmount += frm.doc.items[i].amount;
			}
			// If is_main is 1, assign the sum to the amount and reset the sum
			else if (frm.doc.items[i].is_main === 1) {
				frm.doc.items[i].amount = sumAmount;
				sumAmount = 0;
			}
		}
		frm.clear_table("main_item_summary")
		for(let i=0;i<frm.doc.items.length;i++){
			if(frm.doc.items[i].is_main){
					var row = frm.add_child("main_item_summary");
					row.main_item = frm.doc.items[i].business_item
					row.contract_amount = frm.doc.items[i].amount
			}
		}
		frm.refresh_field("main_item_summary")
	},
    validate(frm){
        if(frm.doc.items){

            if(frm.doc.items.length > 0){
                if(!frm.doc.manual_series){
                    frm.events.set_seriesline(frm);
                }
            }
        }
           
	},
});

frappe.ui.form.on("Subcontractor Contract Item", {
    contract_quantity(frm, cdt, cdn){
        let row = locals[cdt][cdn];
        frape.model.set_value(cdt, cdn, "amount", row.contract_quantity * row.rate);
    },
    rate(frm, cdt, cdn){
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "amount", row.contract_quantity * row.rate);
    },
    business_item(frm, cdt, cdn){
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "project", frm.doc.project);
        frappe.model.set_value(cdt, cdn, "cost_center", frm.doc.cost_center);
        frappe.model.set_value(cdt, cdn, "related_business_item", frm.doc.business_item);
    }
});



function create_subcontractor_clearence(frm){
    frappe.model.with_doctype('Subcontractors Clearence', function() {
        var subcontractors_clearence= frappe.model.get_new_doc('Subcontractors Clearence');
        subcontractors_clearence.subcontractor_contract = frm.doc.name
        subcontractors_clearence.business_item = frm.doc.business_item
        // subcontractors_clearance.transaction_date = frappe.datetime.now_date();
        frm.doc.items.forEach(function(item) {
            if(item.is_main && item.completed_amount < item.max_allowed_amount){
                var subcontractors_clearence_item=frappe.model.add_child(subcontractors_clearence, 'items');
                subcontractors_clearence_item.is_main = item.is_main
                subcontractors_clearence_item.business_item = item.business_item
                subcontractors_clearence_item.description = item.description
                subcontractors_clearence_item.number = item.number
                subcontractors_clearence_item.uom = item.uom
                subcontractors_clearence_item.project = item.project
                subcontractors_clearence_item.related_business_item = item.related_business_item
                subcontractors_clearence_item.cost_center = item.cost_center
                // Contract QTY
                subcontractors_clearence_item.contract_qty = item.max_allowed_qty
                subcontractors_clearence_item.contract_rate = item.rate
                subcontractors_clearence_item.contract_amount = item.max_allowed_amount
                subcontractors_clearence_item.remining_qty = item.remaining__quantity
                subcontractors_clearence_item.remining_amount = item.max_allowed_amount - item.completed_amount
                // current QTY
                subcontractors_clearence_item.current_qty = item.remaining__quantity
                subcontractors_clearence_item.current_rate =item.rate
                subcontractors_clearence_item.current_amount = item.remaining__quantity * item.rate
                // reference
                subcontractors_clearence_item.subcontractor_contract_item_row = item.name


            }
            if(!item.is_main && item.completed_amount < item.max_allowed_amount){
                var subcontractors_clearence_item=frappe.model.add_child(subcontractors_clearence, 'items');
                subcontractors_clearence_item.is_main = item.is_main
                subcontractors_clearence_item.business_item = item.business_item
                subcontractors_clearence_item.description = item.description
                subcontractors_clearence_item.number = item.number
                subcontractors_clearence_item.uom = item.uom
                subcontractors_clearence_item.project = item.project
                subcontractors_clearence_item.related_business_item = item.related_business_item
                subcontractors_clearence_item.cost_center = item.cost_center
                // Contract QTY
                subcontractors_clearence_item.contract_qty = item.max_allowed_qty
                subcontractors_clearence_item.contract_rate = item.rate
                subcontractors_clearence_item.contract_amount = item.max_allowed_amount
                subcontractors_clearence_item.remining_qty = item.remaining__quantity
                subcontractors_clearence_item.remining_amount = item.max_allowed_amount - item.completed_amount
                // current QTY
                subcontractors_clearence_item.current_qty = item.remaining__quantity
                subcontractors_clearence_item.current_rate =item.rate
                subcontractors_clearence_item.current_amount = item.remaining__quantity * item.rate
                // reference
                subcontractors_clearence_item.subcontractor_contract_item_row = item.name
            }
            
        })
        subcontractors_clearence.advance_payment_percentage = frm.doc.advance_payment_percentage
		subcontractors_clearence.first_retention_percentage = frm.doc.first_retention_percentage
		subcontractors_clearence.final_retention_percentage = frm.doc.final_retention_percentage
		subcontractors_clearence.value_added_tax_percentage = frm.doc.value_added_tax_percentage
		subcontractors_clearence.tax_deduction_and_addition_percentage = frm.doc.tax_deduction_and_addition_percentage
        
        frappe.set_route('Form', 'Subcontractors Clearence', subcontractors_clearence.name);

    })
}





function create_payment(frm) {
    let d = new frappe.ui.Dialog({
        title: 'Enter details',
        fields: [
            {
                label: 'Mode of Payment',
                fieldname: 'mode_of_payment',
                fieldtype: 'Link',
                options: 'Mode of Payment',
                reqd: 1
            }
        ],
        size: 'small', // small, large, extra-large 
        primary_action_label: 'Submit',
        primary_action(values) {
            console.log(values);
            d.hide();
            frm.call('create_payment', { mode_of_payment: values.mode_of_payment });
        },
        // Adding a cancel button
        secondary_action_label: 'Cancel',
        secondary_action() {
            d.hide(); // Just hide the dialog
        }
    });
    
    d.show();
}
