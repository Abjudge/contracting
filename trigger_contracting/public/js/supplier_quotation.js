frappe.ui.form.on("Supplier Quotation", {
        
    validate(frm) {
        if (frm.doc.items){
            frm.doc.items.forEach((row)=>{
            row.project = frm.doc.project
            })
        }
    }
})