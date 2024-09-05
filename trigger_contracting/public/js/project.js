frappe.ui.form.on("Project", {

	refresh(frm){
		
            frm.add_custom_button('Create Costing Voucher', function() {
				create_costing_voucher(frm)
            });
       
		frm.add_custom_button('Create Quotation', function() {
			create_customer_quotation(frm)
		});
		frm.add_custom_button('Create Customer Contract ', function() {
			create_customer_contract(frm)
		});
		
		
	},
	setup(frm){
        frm.set_query("business_item", "custom_project_items", function (doc, cdt, cdn) {
            let d=locals[cdt,cdn]
            return{
                filters:[
                    ['Business Item', 'project', '=', doc.name]
                ]
            }
            
        })
		
	},
	custom_revenue_setup(frm) {
		frappe.db.get_value('Revenue Setup',frm.doc.custom_revenue_setup,[
			'advance_payment__percentage',
			'first_retention_percentage',
			'final_retention_percentage',
			'value_added_tax_percentage',
			'tax_deduction_and_addition__percentage'
		], (data) => {
			frm.doc.custom_advance_payment__percentage = data.advance_payment__percentage;
			frm.doc.custom_first_retention_percentage = data.first_retention_percentage;
			frm.doc.custom_final_retention_percentage = data.final_retention_percentage;
			frm.doc.custom_value_added_tax_percentage = data.value_added_tax_percentage;
			frm.doc.custom_tax_deduction_and_addition__percentage = data.tax_deduction_and_addition__percentage;
			frm.refresh_fields([
				'custom_advance_payment__percentage',
				'custom_first_retention_percentage',
				'custom_final_retention_percentage',
				'custom_value_added_tax_percentage',
				'custom_tax_deduction_and_addition__percentage'
			]);
		});
	}
	,
	set_seriesline(frm){
		var index = 0
		var subindex = 1
        for(let i=0;i<frm.doc.custom_project_items.length ; i++){
            if(frm.doc.custom_project_items[i].is_main == 1){
				    index +=1 
					subindex = 1
					frm.doc.custom_project_items[i].number = index
            }
            else{
				frm.doc.custom_project_items[i].number = index + "-" + subindex
				subindex = subindex +1
            }
        }
        frm.refresh_field("custom_project_items")
    },
	calc_totals(frm){

		let sumAmount = 0;
		// Iterate over the data in reverse order
		for (let i = frm.doc.custom_project_items.length - 1; i >= 0; i--) {
			// If is_main is 0, add the amount to the sum
			if (frm.doc.custom_project_items[i].is_main === 0) {
				sumAmount += frm.doc.custom_project_items[i].amount;
			}
			// If is_main is 1, assign the sum to the amount and reset the sum
			else if (frm.doc.custom_project_items[i].is_main === 1) {
				frm.doc.custom_project_items[i].amount = sumAmount;
				sumAmount = 0;
			}
		}
		frm.clear_table("project_items_summary")
		for(let i=0;i<frm.doc.custom_project_items.length;i++){
			if(frm.doc.custom_project_items[i].is_main){
					var row = frm.add_child("project_items_summary");
					row.main_item = frm.doc.custom_project_items[i].business_item
					// row.contract_amount = frm.doc.custom_project_items[i].amount
			}
		}
		frm.refresh_field("project_items_summary")
	},
    validate(frm){
		if(!frm.doc.custom_manual_series){
			frm.events.set_seriesline(frm);
		}
		
		frm.events.calc_totals(frm);
	},
});

frappe.ui.form.on("Project Items", {
	quantity(frm,cdt,cdn){
		let row = locals[cdt][cdn];
		row.amount = row.quantity * row.rate
		frm.refresh_fields()
	},
	rate(frm,cdt,cdn){
		let row = locals[cdt][cdn];
		row.amount = row.quantity * row.rate
		frmlds().refresh_fie
	},
});

function create_costing_voucher(frm){
	frappe.model.with_doctype('Costing Voucher', function() {
		var costing_voucher= frappe.model.get_new_doc('Costing Voucher');
		
		costing_voucher.project = frm.doc.name
		costing_voucher.customer = frm.doc.customer
		// costing_voucher.date = frm.doc.date
		costing_voucher.custom_tender_number = frm.doc.custom_tender_number
		frm.doc.custom_project_items.forEach(function(item) {
			var costing_voucher_item=frappe.model.add_child(costing_voucher, 'costing_voucher_items');
			costing_voucher_item.business_item = item.business_item
			// costing_voucher_item.amount = item.amount
			costing_voucher_item.is_main = item.is_main
			costing_voucher_item.description = item.description
			costing_voucher_item.number = item.number
			costing_voucher_item.uom = item.uom
			costing_voucher_item.quantity = item.quantity
			// costing_voucher_item.amount = item.amount
			costing_voucher_item.project_row_id=item.name
			costing_voucher_item.business_item_name=item.business_item_name

			
		})
		frm.doc.project_items_summary.forEach(function(item) {
			var costing_voucher_main_item=frappe.model.add_child(costing_voucher, 'costing_voucher_main_business_items');
			costing_voucher_main_item.main_business_item = item.main_item
			costing_voucher_main_item.project_id = item.name
			costing_voucher_main_item.business_item_name=item.business_item_name

		})

		frappe.set_route('Form', 'Costing Voucher', costing_voucher.name);
	
	})
}


function create_customer_quotation(frm){
	frappe.model.with_doctype('Customer Quotation', function() {
		var customer_quotation= frappe.model.get_new_doc('Customer Quotation');
		
		customer_quotation.project = frm.doc.name
		customer_quotation.customer = frm.doc.customer
		customer_quotation.company = frm.doc.company
		customer_quotation.cost_center = frm.doc.cost_center
		customer_quotation.advance_payment_percentage = frm.doc.custom_advance_payment__percentage
		customer_quotation.first_retention_percentage = frm.doc.custom_first_retention_percentage
		customer_quotation.final_retention_percentage = frm.doc.custom_final_retention_percentage
		customer_quotation.value_added_tax_percentage = frm.doc.custom_value_added_tax_percentage
		customer_quotation.tax_deduction_and_addition_percentage = frm.doc.custom_tax_deduction_and_addition__percentage

		customer_quotation.custom_tender_number = frm.doc.custom_tender_number
		frm.doc.custom_project_items.forEach(function(item) {
			var customer_quotation_item=frappe.model.add_child(customer_quotation, 'items');
			customer_quotation_item.business_item = item.business_item
			customer_quotation_item.amount = item.amount
			customer_quotation_item.is_main = item.is_main
			customer_quotation_item.description = item.description
			customer_quotation_item.number = item.number
			customer_quotation_item.uom = item.uom
			customer_quotation_item.quantity = item.quantity
			customer_quotation_item.rate = item.rate
			customer_quotation_item.amount = item.amount
		
			customer_quotation_item.business_item_name = item.business_item_name

			
		})

		frappe.set_route('Form', 'Customer Quotation', customer_quotation.name);
	
	})

}

function create_customer_contract(frm){
	frappe.model.with_doctype('Customer Contract', function() {
		var customer_contract= frappe.model.get_new_doc('Customer Contract');
		customer_contract.project = frm.doc.name
		customer_contract.customer = frm.doc.customer
		customer_contract.company = frm.doc.company
		customer_contract.cost_center = frm.doc.cost_center
		customer_contract.advance_payment_percentage = frm.doc.custom_advance_payment__percentage
		customer_contract.first_retention_percentage = frm.doc.custom_first_retention_percentage
		customer_contract.final_retention_percentage = frm.doc.custom_final_retention_percentage
		customer_contract.value_added_tax_percentage = frm.doc.custom_value_added_tax_percentage
		customer_contract.tax_deduction_and_addition_percentage = frm.doc.custom_tax_deduction_and_addition__percentage
		customer_contract.custom_tender_number = frm.doc.custom_tender_number
		frm.doc.custom_project_items.forEach(function(item) {
			var customer_contract_item=frappe.model.add_child(customer_contract, 'items');
			customer_contract_item.business_item = item.business_item
			customer_contract_item.amount = item.amount
			customer_contract_item.is_main = item.is_main
			customer_contract_item.description = item.description
			customer_contract_item.number = item.number
			customer_contract_item.uom = item.uom
			customer_contract_item.contract_quantity = item.quantity
			customer_contract_item.rate = item.rate
			customer_contract_item.cost_center = frm.doc.cost_center
			customer_contract_item.project = frm.doc.project


	})
	

		frappe.set_route('Form', 'Customer Contract', customer_contract.name);
	
	})
}