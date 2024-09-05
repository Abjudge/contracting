frappe.form.link_formatters['Business Item'] = function(value, doc) {
    if(doc.business_item_name && doc.business_item_name !== value) {
        return value + ': ' + doc.business_item_name;
    } else {
        return value;
    }
}

frappe.form.link_formatters['Subcontractor Business Item'] = function(value, doc) {
    if(doc.business_item_name && doc.business_item_name !== value) {
        return value + ': ' + doc.business_item_name;
    } else {
        return value;
    }
}