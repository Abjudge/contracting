// Copyright (c) 2024, TS and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Submitted Invoice", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Submitted Invoice Item", {
	current_qty(frm,cdt,cdn) {
        let row = locals[cdt][cdn];
        // console.log(row.current_qty)
        if(row.is_main ==0){
            if(row.current_qty <= 0 || row.current_qty > row.current_saved_qty){
                frappe.model.set_value(cdt,cdn,'current_qty',row.current_saved_qty)
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

