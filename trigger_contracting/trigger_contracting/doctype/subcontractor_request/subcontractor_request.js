// Copyright (c) 2024, TS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Subcontractor Request", {
	setup: function(frm) {
		frm.set_query("customer_business_item", "subcontractor_request_items", function(doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
                query: "trigger_contracting.trigger_contracting.doctype.subcontractor_request.subcontractor_request.get_customer_business_item",
				filters: {
                    "project": frm.doc.project
                }
            };
        });
        
	},
    refresh: function(frm) {
        if(frm.doc.docstatus == 0){
            frm.set_value("requester",frappe.user.full_name())
        }
        if(frm.doc.docstatus == 1){
            frm.add_custom_button(__('Create Subcontractor Contract'), function() {
                create_subcontractor_contract(frm);
            });
        }
    }
});

frappe.ui.form.on("Subcontractor Request Items", {
    customer_business_item(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if(row.customer_business_item){
            frappe.db.get_doc("Project", frm.doc.project).then(doc => {
                doc.custom_project_items.forEach(item => {
                    if(item.business_item == row.customer_business_item){
                        frappe.model.set_value(cdt, cdn, "qty", item.quantity);
                        frappe.model.set_value(cdt, cdn, "number", item.number);
                        frappe.model.set_value(cdt, cdn, "unit", item.uom);
                    }
                });  
            });                      
        }
    }
});

function create_subcontractor_contract(frm){
    frappe.model.with_doctype('Subcontractor Contract', function() {
        let doc = frappe.model.get_new_doc("Subcontractor Contract");
        doc.project = frm.doc.project;
        doc.subcontractor_request = frm.doc.name;
        doc.cost_center = frm.doc.cost_center;
        doc.terms_and_condition = frm.doc.terms_and_condition;
        frappe.set_route('Form', 'Subcontractor Contract', doc.name);
    }); 
}
