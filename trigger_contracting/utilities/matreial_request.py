import frappe
from frappe import _
from frappe.utils import flt
import json

def submite(doc,doc_event):
    if doc.project_required_material:
        for row in doc.items:
            item = frappe.get_doc("Project Required Material Item", row.row_id)
            item.requested_quantity = (item.requested_quantity or 0) + row.qty
            item.remaining_quantity= (item.remaining_quantity or 0) - row.qty
            item.save()

def cancel(doc,doc_event):
    if doc.project_required_material:
        for row in doc.items:
            item = frappe.get_doc("Project Required Material Item", row.row_id)
            item.requested_quantity = (item.requested_quantity or 0) - row.qty
            item.remaining_quantity= (item.remaining_quantity or 0) + row.qty
            item.save()


# custom Filter On Room Field that we want To get Available Rooms that not used on Course schedual in Booking Request
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def room_filter(doctype, txt, searchfield, start, page_len, filters):
    if isinstance(filters, str) :
        filters = json.loads(filters)
    return frappe.db.sql("""select name,platform,room_name,seating_capacity from `tabRoom` where platform = '{key}' and name not in (select room from `tabCourse Schedule` where room IS NOT NULL and schedule_date = '{date}' and to_time > '{time}');""".format(**{
            'key': filters["platform"],
            'date':filters["date"],
            'time' :filters["time"],
        }), 
        {
        'txt': "%{}%".format(txt),
        '_txt': txt.replace("%", ""),
        'start': start,
        'page_len': page_len})



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def business_item_filter(doctype, txt, searchfield, start, page_len, filters):
    if isinstance(filters, str) :
        filters = json.loads(filters)
    return frappe.db.sql("""select business_item , business_item_name from `tabProject Items` where parent = '{key}';""".format(**{
            'key': filters.get("project") or ""
        }), 
        {
        'txt': "%{}%".format(txt),
        '_txt': txt.replace("%", ""),
        'start': start,
        'page_len': page_len})


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_group_filter(doctype, txt, searchfield, start, page_len, filters):
    if isinstance(filters, str) :
        filters = json.loads(filters)
    return frappe.db.sql("""select `tabProject Required Material Item`.item_group,`tabItem Group`.parent_item_group from `tabProject Required Material Item` inner join `tabItem Group` on `tabItem Group`.name = `tabProject Required Material Item`.item_group inner join `tabProject Required Material` on `tabProject Required Material`.name = `tabProject Required Material Item`.parent and  `tabProject Required Material`.project = '{key}';""".format(**{
            'key': filters.get("project") or "" 
        }), 
        {
        'txt': "%{}%".format(txt),
        '_txt': txt.replace("%", ""),
        'start': start,
        'page_len': page_len})