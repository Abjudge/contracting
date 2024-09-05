// Copyright (c) 2024, TS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Subcontractors Clearence", {
    refresh(frm) {
            if (frm.doc.docstatus == 1) {
                frm.add_custom_button(__('Create Journal Entry'), function() {  
                    if(frm.doc.journal_created == 0){
                        frappe.call({
                            method: "trigger_contracting.trigger_contracting.doctype.subcontractors_clearence.subcontractors_clearence.create_journal_entry",
                            args: {
                                doc: frm.doc
                            },
                            // callback: function(r) {
                            //     frappe.set_route("Form", "Journal Entry", r.message);
                            // }
                        });
                        frm.reload_doc();
                    }
                    else{
                        frappe.msgprint('You already created Journal Entry for this Clearence , cannot Create Again')
                    }
                });
            }
    },
    setup(frm) {
        frm.set_query('deduction_name', 'deductions', function(doc, cdt, cdn) {
            return {
                filters: {
                    'type': 'Subcontractors'
                    
                }
            };
        });
        frm.set_query('addition_name', 'additions', function(doc, cdt, cdn) {
            return {
                filters: {
                    'type': 'Subcontractors'
                    
                }
            };
        });
    },
});
frappe.ui.form.on("S-Clearence Item", {
    current_qty(frm,cdt,cdn) {
        let row = locals[cdt][cdn];
        if(row.is_main ==0){
            if(row.current_qty <= 0 || row.current_qty > row.remining_qty){
                frappe.model.set_value(cdt,cdn,'current_qty',row.remining_qty)
                frappe.msgprint('Current QTY must be greater than 0 and less than or equal to the Remining QTY')
                
            }
            else{
                frappe.model.set_value(cdt,cdn,'current_percentage',row.current_qty/row.contract_qty*100)
            }
        }
        
	},
    current_percentage(frm,cdt,cdn) {
        let row = locals[cdt][cdn];
        if(row.is_main ==0){
            frappe.model.set_value(cdt,cdn,'current_qty',row.contract_qty*row.current_percentage/100)
        }
    }
});

