// Copyright (c) 2024, TS and contributors
// For license information, please see license.txt

frappe.ui.form.on("BOQ", {
	onload(frm) {
        // sum_total_material_cost(frm)
        // sum_labor_cost(frm)
        // sum_total_required_equipment_cost(frm)
        // sum_total_subcontractors_cost(frm)
        // sum_other_expenses_cost(frm)
	},
    // filters on all childs tables
    setup(frm){
        frm.set_query("item_code", "boq_item", function (doc, cdt, cdn) {
            let d=locals[cdt,cdn]
            return{
                filters:[
                    ['Item', 'is_stock_item', '=', 1]
                ]
            }
            
        })
        frm.set_query("item_code", "labor_table", function (doc, cdt, cdn) {
            let row=locals[cdt,cdn]
            return{
                filters:[
                    ['Item', 'is_stock_item', '=', 0],
                    ['Item', 'is_labor_cost', '=', 1]
                ]
            }
            
        })
        
        frm.set_query("item", "required_equipment", function (doc, cdt, cdn) {
            let d=locals[cdt,cdn]
            return{
                filters:[
                    ['Item', 'is_equipment', '=', 1]
                ]
            }
            
        })
        frm.set_query("item_code", "other_expenses", function (doc, cdt, cdn) {
            let d=locals[cdt,cdn]
            return{
                filters:[
                    // ['Item', 'is_stock_item', '=', 0],
                    // ['Item', 'is_equipment', '=', 0],
                    // ['Item', 'is_labor_cost', '=', 0],
                    ['Item', 'is_expenses', '=', 1]

                ]
            }
            
        })
        

    },

});
// All functions on BOQ Item child table
frappe.ui.form.on("BOQ Item", {
	quantity(frm,cdt,cdn){
		let row = locals[cdt][cdn];
		row.amount = row.quantity * row.rate
		frm.refresh_fields()
        // sum_total_material_cost(frm) 
	},
	rate(frm,cdt,cdn){
		let row = locals[cdt][cdn];
		row.amount = row.quantity * row.rate
		frm.refresh_fields()
        // sum_total_material_cost(frm)
	},
    // boq_item_remove(frm,cdt,cdn){
    //     let row = locals[cdt][cdn];
    //     // sum_total_material_cost(frm)
    // }
 
});
// function sum_total_material_cost(frm){
//     if(frm.doc.boq_item){
//         frm.doc.total_material_cost=0
//         frm.doc.boq_item.forEach((row)=>{
//             frm.doc.total_material_cost += row.amount
//         })
//         frm.refresh_field("total_material_cost")
//     }
// }
// All functions on BOQ labor child table
frappe.ui.form.on("BOQ Labor Table", {
amount(frm,cdt,cdn){
    let row = locals[cdt][cdn];
    // sum_labor_cost(frm)
},
// labor_table_remove(frm,cdt,cdn){
//     let row=locals[cdt][cdn]
//     // sum_labor_cost(frm)
// }

})

// All functions on BOQ Required Equipment child table
frappe.ui.form.on("BOQ Required Equipment", {
    quantity(frm,cdt,cdn){
		let row = locals[cdt][cdn];
		row.amount = row.quantity * row.rate
		frm.refresh_fields()
	},
	rate(frm,cdt,cdn){
		let row = locals[cdt][cdn];
		row.amount = row.quantity * row.rate
		frm.refresh_fields()
	}
    
    
})


// all functions on BOQ Subcontractors
frappe.ui.form.on("BOQ Subcontractors", {
    // amount(frm,cdt,cdn){
    //     let row = locals[cdt][cdn];
    //     sum_total_subcontractors_cost(frm)
    // },
    // subcontractors_remove(frm,cdt,cdn){
    //     let row=locals[cdt][cdn]
    //     sum_total_subcontractors_cost(frm)
    // }

    
})



frappe.ui.form.on("BOQ Other Expenses",{
    quantity(frm,cdt,cdn){
		let row = locals[cdt][cdn];
		row.amount = row.quantity * row.rate
		frm.refresh_fields()
	},
	rate(frm,cdt,cdn){
		let row = locals[cdt][cdn];
		row.amount = row.quantity * row.rate
		frm.refresh_fields()
       
	}


})

