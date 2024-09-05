// Copyright (c) 2024, TS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Addition Item", {
	setup: function(frm) {
		frm.set_query("account", "addition_item_accounts", function(doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					['Account', 'is_group', '=', 0],
					['Account', 'company', '=', d.company]
				]
            }
        });
	},
});
