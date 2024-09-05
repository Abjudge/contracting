import frappe
def submit_journal_entry(doc,doc_event):
    if doc.custom_subcontractors_clearence:
        frappe.db.set_value("Subcontractors Clearence", doc.custom_subcontractors_clearence, "journal_created", 1)
        frappe.db.commit()
    if doc.custom_customer_clearence:
        frappe.db.set_value("Customer Clearence", doc.custom_customer_clearence, "journal_created", 1)
        frappe.db.commit()

def cancel_journal_entry(doc,doc_event):
    if doc.custom_subcontractors_clearence:
        frappe.db.set_value("Subcontractors Clearence", doc.custom_subcontractors_clearence, "journal_created", 0)
        frappe.db.commit()
    if doc.custom_customer_clearence:
        frappe.db.set_value("Customer Clearence", doc.custom_customer_clearence, "journal_created", 0)
        frappe.db.commit()


        
