// Copyright (c) 2024, TS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Revenue Setup", {
	setup(frm) {
        set_account_filter(frm, "accrual_revenue_account")
        set_account_filter(frm, "revenue_account")
        set_account_filter(frm, "value_added_tax_account")
        set_account_filter(frm, "tax_deduction_and_addition_account")
        set_account_filter(frm, "business_insurance_account")
        set_account_filter(frm, "advance_payment_account")
    },
        
});


function set_account_filter(frm,fieldname) {
    frm.set_query(fieldname, function() {
        return {
            filters: {
                company: frm.doc.company,
                is_group: 0
            }
        };
    });
}
