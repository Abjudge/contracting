frappe.ui.form.on("Request for Quotation", {
    validate(frm) {
        if (frm.doc.items){
            frm.doc.items.forEach((row)=>{
            row.project_name = frm.doc.project
            })
        }
    }
})

