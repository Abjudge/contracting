// Copyright (c) 2024, TS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Costing Voucher", {
    setup(frm){
        frm.set_query("item_code", "costing_voucher_indirect_cost", function (doc, cdt, cdn) {
            let d=locals[cdt,cdn]
            return{
                filters:[
                    ['Item', 'custom_is_indirect_cost', '=', 1]
                ]
            }
            
        })
        frm.set_query("item_code", "costing_voucher_markup_cost", function (doc, cdt, cdn) {
            let d=locals[cdt,cdn]
            return{
                filters:[
                    ['Item', 'custom_is_markup_cost', '=', 1]
                ]
            }
            
        })

    },
	onload(frm) {
        
    //     if(frm.doc.costing_voucher_items){
    //         frm.doc.costing_voucher_items.forEach((item)=>{
    //             if(item.is_main){
    //                 frm.doc.costing_voucher_main_business_items.forEach((row)=>{
    //                     if(row.main_business_item==item.business_item){
    //                         row.item_id=item.idx  
    //                     }
    //                 })
    //             }
    //         })
        

	// }
    },
    before_submit(frm){
        if(frm.doc.costing_voucher_items){
            var not_done =[]
            frm.doc.costing_voucher_items.forEach((item)=>{
                if(!item.is_main)
                if (!item.boq_id){
                    not_done.push(item)

                }
            })
            if(not_done.length>0){
                not_done.forEach((item)=>{
                    frappe.msgprint(`Please create BOQ for ${item.business_item} In Row ID ${item.idx} `)    
                })
                frappe.throw("Please create BOQ")
            }
        }

    },
    // validate(frm){
        
    //     // calc amount and selling_amount of costing_voucher_items 
    //     if(frm.doc.costing_voucher_items){
    //         frm.doc.costing_voucher_items.forEach((item)=>{
    //             if(!item.is_main&&item.rate&&item.quantity){
    //                 item.amount = item.rate * item.quantity

    //             }
    //             if(!item.is_main&&item.rate&&item.quantity&&item.margin){
    //                 item.selling_amount = item.amount * (1+(item.margin/100))
    //                 item.selling_rate=item.selling_amount/item.quantity

    //             }
    //         })
    //     }

    //     calc_main_items(frm)
    //     // fich costing_voucher_main_business_items values 
    //     for(let i=0;i<frm.doc.costing_voucher_items.length;i++){
    //         if(frm.doc.costing_voucher_items[i].is_main&&frm.doc.costing_voucher_items[i+1].is_main){
    //             frm.doc.costing_voucher_items[i].amount=frm.doc.costing_voucher_items[i+1].amount
    //             frm.doc.costing_voucher_items[i].rate=frm.doc.costing_voucher_items[i+1].rate
    //             frm.doc.costing_voucher_items[i].selling_amount=frm.doc.costing_voucher_items[i+1].selling_amount
    //         }
    //     }
    //     frm.doc.costing_voucher_items.forEach((item)=>{
    //         if(item.is_main){
    //            frm.doc.costing_voucher_main_business_items.forEach((row)=>{
    //                if(row.item_id==item.idx){
    //                 row.cost=item.amount
    //                    row.selling_price = item.selling_amount
    //                    row.profit=row.selling_price-row.cost
    //                    row.profit_percentage=(row.selling_price/row.cost)
    //                    frm.refresh_field("costing_voucher_main_business_items")
    //                    frm.refresh_fields()
    //                }
    //            })
    //         }
    //     })
       


        
//     }
//     ,margin(frm){
//         if(frm.doc.costing_voucher_items){  
//             frm.doc.costing_voucher_items.forEach((item)=>{
//                 if(!item.is_main)
//                 item.margin = frm.doc.margin
//             })
//         }
   
// }

});

frappe.ui.form.on("Costing Voucher Items", {
    boq(frm,cdt,cdn){
        let row=locals[cdt][cdn]
        if(!row.is_main){
            create_boq(frm,row)
        }
      
        
    }
})

function create_boq(frm,row){
    var boq= frappe.model.get_new_doc('BOQ');
    boq.costing_voucher=frm.doc.name
    boq.row_id=row.row_id
    boq.transaction_date=frm.doc.date
    boq.related_project=frm.doc.project
    boq.related_customer=frm.doc.customer
    boq.project_row_id=row.project_row_id
    boq.c_v_row_id=row.name
    boq.project__quantity=row.quantity
    boq.business_item=row.business_item
   for(i=row.idx;i>0;i--){
    if(frm.doc.costing_voucher_items[i-1].is_main){
        boq.main_b_i=frm.doc.costing_voucher_items[i-1].business_item
        break
    }
    
   }
   
    frappe.set_route('Form', 'BOQ', boq.name);

}

// function calc_main_items(frm){
//     let total_amount=0
//     // let total_rate=0
//     let total_selling_amount=0
    
//     for(let i=frm.doc.costing_voucher_items.length -1;i>=0;i--){
// 		if(!frm.doc.costing_voucher_items[i].is_main&&frm.doc.costing_voucher_items[i].rate&&frm.doc.costing_voucher_items[i].amount&&frm.doc.costing_voucher_items[i].selling_amount){
// 			total_amount+=frm.doc.costing_voucher_items[i].amount
//             // total_rate+=frm.doc.costing_voucher_items[i].rate
//             total_selling_amount+=frm.doc.costing_voucher_items[i].selling_amount
           
// 		} else if(frm.doc.costing_voucher_items[i].is_main){
//             frm.doc.costing_voucher_items[i].amount=total_amount;
//             total_amount=0;
//             // frm.doc.costing_voucher_items[i].rate=total_rate;
//             // total_rate=0;
//             frm.doc.costing_voucher_items[i].selling_amount=total_selling_amount;
//             total_selling_amount=0;
//         }
//     }
// }
