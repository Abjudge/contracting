// Copyright (c) 2024, TS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project Required Material", {
	refresh(frm) {
        
        frm.add_custom_button("Create Material Request", function () {
            create_material_request(frm)
            // frm.get_selected().items.forEach(function(item) {
            //     console.log(item)
            // });
          

        })
	},
    onload(frm){
        
    }
});

function create_material_request(frm) {
    frappe.model.with_doctype('Material Request', function() {
		var material_request_doc = frappe.model.get_new_doc('Material Request');
        material_request_doc.project = frm.doc.project;
        material_request_doc.project_required_material = frm.doc.name;
        if(frm.get_selected().items){
        frm.doc.items.forEach(function(item) {
            frm.get_selected().items.forEach(function(selected_item) {
                if(selected_item == item.name){
                    var material_request_item=frappe.model.add_child(material_request_doc, 'items');
                    material_request_item.item_code = item.item_code
                    material_request_item.row_id = item.name
                    material_request_item.qty = item.remaining_quantity
                    material_request_item.rqty = item.remaining_quantity
                }
            })
        })
    }else if(!frm.get_selected().items){
        frappe.throw("please Select Items ")
    }
        frappe.set_route('Form', 'Material Request', material_request_doc.name);
    });
 
    };