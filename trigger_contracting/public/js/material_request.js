frappe.ui.form.on("Material Request", {
    setup: function(frm) {
        frm.set_query("custom_p_item_group", "items",function(doc,cdt,cdn){
            let d=locals[cdt][cdn]
            return {
                query: "trigger_contracting.utilities.matreial_request.item_group_filter",
                filters: {
                    "project": frm.doc.project || ""
                }
            }
        });
        frm.set_query("item_code", "items",function(doc,cdt,cdn){
            let d=locals[cdt][cdn]
            return {
                filters: {
                    "item_group": d.custom_p_item_group
                }
            }
        });

    },
    refresh: function(frm) {
           
                frm.set_query("business_item", "items", function (doc, cdt, cdn) {
                    let d = locals[cdt][cdn];
                    return {
                        query: "trigger_contracting.utilities.matreial_request.business_item_filter",
                        filters: {
                            "project": frm.doc.project || ""
                        }
                    };
                });
            

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
    validate(frm){
        for(let i=0;i<frm.doc.items.length;i++){
            if(frm.doc.items[i].rqty){
                if(frm.doc.items[i].qty>frm.doc.items[i].rqty){
                    frappe.throw(` At Row ${frm.doc.items[i].idx} Quantity can not be more than ${frm.doc.items[i].rqty}`)
                    break
                }  
            }

        }

    },

    type(frm) {
        frm.clear_table("items");
        if (frm.doc.type == 'Material') {
            frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                let d = locals[cdt][cdn];
                return {
                    filters: [
                        ['Item', 'is_stock_item', '=', 1],
                        ['Item', 'item_group', '=', d.custom_p_item_group]
                    ]
                };
            });
            frm.refresh_field("items");
        } else if (frm.doc.type == 'Asset') {
            frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                let d = locals[cdt][cdn];
                return {
                    filters: [
                        ['Item', 'is_fixed_asset', '=', 1],
                        ['Item', 'item_group', '=', d.custom_p_item_group]
                    ]
                };
            });
            frm.refresh_field("items");
        } else if (frm.doc.type == 'Service') {
            frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                let d = locals[cdt][cdn];
                return {
                    filters: [
                        ['Item', 'is_fixed_asset', '=', 0],
                        ['Item', 'is_stock_item', '=', 0],
                        ['Item', 'item_group', '=', d.custom_p_item_group]
                    ]
                };
            });
            frm.refresh_field("items");
        }
    }
});

frappe.ui.form.on("Material Request Item", {
    qty(frm,cdt,cdn){
        let row=locals[cdt][cdn] 
        if(row.rqty){
            if (row.qty>row.rqty){
            frappe.throw(`Quantity can not be more than ${row.rqty}`)
    }

        }  

    },
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Set the cost center from the parent document to the child table row
        row.cost_center = frm.doc.cost_center;
        row.project = frm.doc.project;
        row.business_item=frm.doc.business_item

        // Refresh the field to update the UI
        frm.refresh_field("items");
    },
    custom_p_item_group: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Set the cost center from the parent document to the child table row
        row.cost_center = frm.doc.cost_center;
        row.project = frm.doc.project;

        // Refresh the field to update the UI
        frm.refresh_field("items");
    }
})
