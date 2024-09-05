// Copyright (c) 2024, TS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer Contract", {
	refresh(frm) {
        if (frm.doc.docstatus == 1) { 
            frm.add_custom_button('Virtual Invoice', function() {
                create_internal_customer_clearence(frm)
            });

            // frm.add_custom_button('Create Submitted Invoice', function() {
                
            //     create_submitted_invoice(frm)
            // });
            frm.add_custom_button('Create Approved Invoice', function() {
                create_customer_clearence(frm,"")
            })
        }
	},
    // validate(frm) {
    //     frm.clear_table("stamps")
    //     frappe.db.get_value('Revenue Setup', { company: frm.doc.company }, 'stamps')
    //         .then((res) => {
    //             if (res.message) {
    //                 console.log(res.message);
    //                 console.log(res);
    //                 // console.log(res.message.stamps);

    //                 // res.message.stamps.forEach((stamp) => {
    //                 //     let row=frm.add_child("stamps")
    //                 //     row.stamp=stamp.stamp
    //                 //     row.percentage=stamp.percentage
    //                 //     row.account=stamp.account
    //                 // })
    //                 frm.refresh_field("stamps");
    //             } else {
    //                 frappe.msgprint(__('No Revenue Setup found for the selected company.'));
    //             }
    //         })
    //         .catch((error) => {
    //             console.error('Error fetching Revenue Setup:', error);
    //             frappe.msgprint(__('There was an error retrieving the Revenue Setup.'));
    //         });
    // }
});
frappe.ui.form.on("Customer Contract Refrances", {
    create_customer_clearence(frm, cdt, cdn){
        let row = locals[cdt][cdn]
        if(row.internal_customer_clearance && row.submitted_invoice && !row.customer_clearence){
            create_customer_clearence(frm,row.internal_customer_clearance)
        }
        
       
    },
    create_submitted_invoice(frm, cdt, cdn){
        let row = locals[cdt][cdn]
        if(row.internal_customer_clearance && !row.submitted_invoice){
            create_submitted_invoice(frm,row.internal_customer_clearance)
        }
        
       
    }



});


function create_internal_customer_clearence(frm){
    frappe.model.with_doctype('Internal Customer Clearance', function() {
        var customer_clearence= frappe.model.get_new_doc('Internal Customer Clearance');
        customer_clearence.customer_contract = frm.doc.name
        frm.doc.items.forEach(function(item) {
            if(item.is_main && item.completed_amount < item.max_allowed_amount){
                var customer_clearence_item=frappe.model.add_child(customer_clearence, 'items');
                customer_clearence_item.is_main = item.is_main
                customer_clearence_item.business_item = item.business_item
                customer_clearence_item.description = item.description
                customer_clearence_item.number = item.number
                customer_clearence_item.uom = item.uom
                customer_clearence_item.project = frm.doc.project
                customer_clearence_item.cost_center = frm.doc.cost_center
                customer_clearence_item.business_item_name = item.business_item_name
                customer_clearence_item.selling_price = item.selling_price

                // Contract QTY
                customer_clearence_item.contract_qty = item.max_allowed_qty
                customer_clearence_item.contract_rate = item.rate
                customer_clearence_item.contract_amount = item.max_allowed_amount
                customer_clearence_item.remining_qty = item.remaining__quantity
                customer_clearence_item.remining_amount = item.max_allowed_amount - item.completed_amount
                // current QTY
                customer_clearence_item.current_qty = item.remaining__quantity
                customer_clearence_item.current_saved_qty = item.remaining__quantity
                customer_clearence_item.current_rate =item.rate
                customer_clearence_item.current_amount = item.remaining__quantity * item.rate
                // reference
                customer_clearence_item.customer_contract_item_row = item.name
               


            }
            if(!item.is_main && item.completed_amount < item.max_allowed_amount){
                var customer_clearence_item=frappe.model.add_child(customer_clearence, 'items');
                customer_clearence_item.is_main = item.is_main
                customer_clearence_item.business_item = item.business_item
                customer_clearence_item.description = item.description
                customer_clearence_item.number = item.number
                customer_clearence_item.uom = item.uom
                customer_clearence_item.project = frm.doc.project
                // customer_clearence_item.selling_price = frm.doc.selling_price
                customer_clearence_item.cost_center = frm.doc.cost_center
                // Contract QTY
                customer_clearence_item.contract_qty = item.max_allowed_qty
                customer_clearence_item.contract_rate = item.rate
                customer_clearence_item.contract_amount = item.max_allowed_amount
                customer_clearence_item.remining_qty = item.remaining__quantity
                customer_clearence_item.remining_amount = item.max_allowed_amount - item.completed_amount
                // current QTY
                customer_clearence_item.current_qty = item.remaining__quantity
                customer_clearence_item.current_saved_qty = item.remaining__quantity
                customer_clearence_item.current_rate =item.rate
                customer_clearence_item.current_amount = item.remaining__quantity * item.rate
                // reference
                customer_clearence_item.customer_contract_item_row = item.name
                customer_clearence_item.business_item_name = item.business_item_name
            }
            
        })
        customer_clearence.advance_payment_percentage = frm.doc.advance_payment_percentage
		customer_clearence.first_retention_percentage = frm.doc.first_retention_percentage
		customer_clearence.final_retention_percentage = frm.doc.final_retention_percentage
		customer_clearence.value_added_tax_percentage = frm.doc.value_added_tax_percentage
		customer_clearence.tax_deduction_and_addition_percentage = frm.doc.tax_deduction_and_addition_percentage
        frm.doc.stamps.forEach(function(stamp) {
            var customer_clearence_stamp=frappe.model.add_child(customer_clearence, 'stamps');
            customer_clearence_stamp.stamp = stamp.stamp
            customer_clearence_stamp.percentage = stamp.percentage
            customer_clearence_stamp.account = stamp.account
            
        })

        
        frappe.set_route('Form', 'Internal Customer Clearance', customer_clearence.name);

    })
}


function create_customer_clearence(frm,internal_customer_clearance){
    frappe.model.with_doctype('Customer Clearence', function() {
        var customer_clearence= frappe.model.get_new_doc('Customer Clearence');
        customer_clearence.customer_contract = frm.doc.name
        customer_clearence.internal_customer_clearance = internal_customer_clearance
        frm.doc.items.forEach(function(item) {
            if(item.is_main && item.completed_amount < item.max_allowed_amount){
                var customer_clearence_item=frappe.model.add_child(customer_clearence, 'items');
                customer_clearence_item.is_main = item.is_main
                customer_clearence_item.business_item = item.business_item
                customer_clearence_item.description = item.description
                customer_clearence_item.number = item.number
                customer_clearence_item.uom = item.uom
                customer_clearence_item.project = frm.doc.project
                customer_clearence_item.cost_center = frm.doc.cost_center
                customer_clearence_item.business_item_name = item.business_item_name
                customer_clearence_item.selling_price = item.selling_price
            

                
               

                // Contract QTY
                customer_clearence_item.contract_qty = item.max_allowed_qty
                customer_clearence_item.contract_rate = item.rate
                customer_clearence_item.contract_amount = item.max_allowed_amount
                customer_clearence_item.remining_qty = item.remaining__quantity
                customer_clearence_item.remining_amount = item.max_allowed_amount - item.completed_amount
                // current QTY
                customer_clearence_item.current_qty = item.remaining__quantity
                customer_clearence_item.current_saved_qty = item.remaining__quantity
                customer_clearence_item.current_rate =item.rate
                customer_clearence_item.current_amount = item.remaining__quantity * item.rate
                // reference
                customer_clearence_item.customer_contract_item_row = item.name
               


            }
            if(!item.is_main && item.completed_amount < item.max_allowed_amount){
                var customer_clearence_item=frappe.model.add_child(customer_clearence, 'items');
                customer_clearence_item.is_main = item.is_main
                customer_clearence_item.business_item = item.business_item
                customer_clearence_item.description = item.description
                customer_clearence_item.number = item.number
                customer_clearence_item.uom = item.uom
                customer_clearence_item.project = frm.doc.project
                customer_clearence_item.rate = item.rate
                // customer_clearence_item.selling_price = frm.doc.selling_price
                customer_clearence_item.cost_center = frm.doc.cost_center
                // Contract QTY
                customer_clearence_item.contract_qty = item.max_allowed_qty
                customer_clearence_item.contract_rate = item.rate
                customer_clearence_item.contract_amount = item.max_allowed_amount
                customer_clearence_item.remining_qty = item.remaining__quantity
                customer_clearence_item.remining_amount = item.max_allowed_amount - item.completed_amount
                // current QTY
                customer_clearence_item.current_qty = item.remaining__quantity
                customer_clearence_item.current_saved_qty = item.remaining__quantity
                customer_clearence_item.current_rate =item.rate
                customer_clearence_item.current_amount = item.remaining__quantity * item.rate
                // reference
                customer_clearence_item.customer_contract_item_row = item.name
                customer_clearence_item.business_item_name = item.business_item_name
            }
            
        })
        customer_clearence.advance_payment_percentage = frm.doc.advance_payment_percentage
		customer_clearence.first_retention_percentage = frm.doc.first_retention_percentage
		customer_clearence.final_retention_percentage = frm.doc.final_retention_percentage
		customer_clearence.value_added_tax_percentage = frm.doc.value_added_tax_percentage
		customer_clearence.tax_deduction_and_addition_percentage = frm.doc.tax_deduction_and_addition_percentage

        frm.doc.stamps.forEach(function(stamp) {
            var customer_clearence_stamp = frappe.model.add_child(customer_clearence, 'stamps');
            customer_clearence_stamp.stamp = stamp.stamp
            customer_clearence_stamp.percentage = stamp.percentage
            customer_clearence_stamp.account = stamp.account
        })
        
        frappe.set_route('Form', 'Customer Clearence', customer_clearence.name);

    })
}

function create_submitted_invoice(frm,internal_customer_clearance){
    frappe.model.with_doctype('Submitted Invoice', function() {
        var submitted_invoice = frappe.model.get_new_doc('Submitted Invoice');
        submitted_invoice.customer_contract = frm.doc.name;
        submitted_invoice.internal_customer_clearance = internal_customer_clearance
        
        frm.doc.items.forEach(function(item) {
            if(item.is_main && item.completed_amount < item.max_allowed_amount){
                var submitted_invoice_item = frappe.model.add_child(submitted_invoice, 'items');
                submitted_invoice_item.is_main = item.is_main;
                submitted_invoice_item.business_item = item.business_item;
                submitted_invoice_item.description = item.description;
                submitted_invoice_item.number = item.number;
                submitted_invoice_item.uom = item.uom;
                submitted_invoice_item.project = frm.doc.project;
                submitted_invoice_item.cost_center = frm.doc.cost_center;
                submitted_invoice_item.business_item_name = item.business_item_name;
                submitted_invoice_item.selling_price = item.selling_price;

                // Contract QTY
                submitted_invoice_item.contract_qty = item.max_allowed_qty;
                submitted_invoice_item.contract_rate = item.rate;
                submitted_invoice_item.contract_amount = item.max_allowed_amount;
                submitted_invoice_item.remining_qty = item.remaining__quantity;
                submitted_invoice_item.remining_amount = item.max_allowed_amount - item.completed_amount;
                // Current QTY
                submitted_invoice_item.current_qty = item.remaining__quantity;
                submitted_invoice_item.current_saved_qty = item.remaining__quantity;
                submitted_invoice_item.current_rate = item.rate;
                submitted_invoice_item.current_amount = item.remaining__quantity * item.rate;
                // Reference
                submitted_invoice_item.customer_contract_item_row = item.name;
            }
            if(!item.is_main && item.completed_amount < item.max_allowed_amount){
                var submitted_invoice_item = frappe.model.add_child(submitted_invoice, 'items');
                submitted_invoice_item.is_main = item.is_main;
                submitted_invoice_item.business_item = item.business_item;
                submitted_invoice_item.description = item.description;
                submitted_invoice_item.number = item.number;
                submitted_invoice_item.uom = item.uom;
                submitted_invoice_item.project = frm.doc.project;
                submitted_invoice_item.cost_center = frm.doc.cost_center;

                // Contract QTY
                submitted_invoice_item.contract_qty = item.max_allowed_qty;
                submitted_invoice_item.contract_rate = item.rate;
                submitted_invoice_item.contract_amount = item.max_allowed_amount;
                submitted_invoice_item.remining_qty = item.remaining__quantity;
                submitted_invoice_item.remining_amount = item.max_allowed_amount - item.completed_amount;
                // Current QTY
                submitted_invoice_item.current_qty = item.remaining__quantity;
                submitted_invoice_item.current_saved_qty = item.remaining__quantity;
                submitted_invoice_item.current_rate = item.rate;
                submitted_invoice_item.current_amount = item.remaining__quantity * item.rate;
                // Reference
                submitted_invoice_item.customer_contract_item_row = item.name;
                submitted_invoice_item.business_item_name = item.business_item_name;
            }
        });
        
        submitted_invoice.advance_payment_percentage = frm.doc.advance_payment_percentage;
        submitted_invoice.first_retention_percentage = frm.doc.first_retention_percentage;
        submitted_invoice.final_retention_percentage = frm.doc.final_retention_percentage;
        submitted_invoice.value_added_tax_percentage = frm.doc.value_added_tax_percentage;
        submitted_invoice.tax_deduction_and_addition_percentage = frm.doc.tax_deduction_and_addition_percentage;

        frm.doc.stamps.forEach(function(stamp) {
            var submitted_invoice_stamp = frappe.model.add_child(submitted_invoice, 'stamps');
            submitted_invoice_stamp.stamp = stamp.stamp;
            submitted_invoice_stamp.account = stamp.account;
            submitted_invoice_stamp.percentage = stamp.percentage;
        })
        
        frappe.set_route('Form', 'Submitted Invoice', submitted_invoice.name);
    });
}
