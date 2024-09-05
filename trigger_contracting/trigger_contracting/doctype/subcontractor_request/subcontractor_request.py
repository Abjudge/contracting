# Copyright (c) 2024, TS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class SubcontractorRequest(Document):
	pass





@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_customer_business_item(doctype, txt, searchfield, start, page_len, filters):
	if isinstance(filters, str) :
		filters = json.loads(filters)
	return frappe.db.sql("""select main_item as name from `tabProject Items Summary` where parent = '{project}' and parenttype = 'Project';""".format(**{'project': filters["project"]}),{'txt': "%{}%".format(txt),'_txt': txt.replace("%", ""),'start': start,'page_len': page_len})