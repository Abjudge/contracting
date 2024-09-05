app_name = "trigger_contracting"
app_title = "Trigger Contracting"
app_publisher = "TS"
app_description = "Contracting"
app_email = "ahmedosama.dev@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/trigger_contracting/css/trigger_contracting.css"
# app_include_js = "/assets/trigger_contracting/js/trigger_contracting.js"

# include js, css files in header of web template
# web_include_css = "/assets/trigger_contracting/css/trigger_contracting.css"
# web_include_js = "/assets/trigger_contracting/js/trigger_contracting.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "trigger_contracting/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}
fixtures = [
    {
        "dt": "Custom Field", "filters": [["module", "in", ["Trigger Contracting"]]]
    }
]
# include js in page
# page_js = {"page" : "public/js/file.js"}
app_include_js = "contract.bundle.js"
# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {"Project" : "public/js/project.js",
              "Material Request" : "public/js/material_request.js",
              "Request for Quotation" : "public/js/rfq.js",
              "Supplier Quotation" : "public/js/supplier_quotation.js",
              
			  }
              
			  
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "trigger_contracting/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "trigger_contracting.utils.jinja_methods",
# 	"filters": "trigger_contracting.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "trigger_contracting.install.before_install"
# after_install = "trigger_contracting.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "trigger_contracting.uninstall.before_uninstall"
# after_uninstall = "trigger_contracting.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "trigger_contracting.utils.before_app_install"
# after_app_install = "trigger_contracting.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "trigger_contracting.utils.before_app_uninstall"
# after_app_uninstall = "trigger_contracting.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "trigger_contracting.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Material Request": {
		"on_submit": "trigger_contracting.utilities.matreial_request.submite",
		"on_cancel": "trigger_contracting.utilities.matreial_request.cancel",
		
	},
	"Journal Entry": {
		"on_submit": "trigger_contracting.utilities.journal_entery.submit_journal_entry",
		"on_cancel": "trigger_contracting.utilities.journal_entery.cancel_journal_entry",
		
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"trigger_contracting.tasks.all"
# 	],
# 	"daily": [
# 		"trigger_contracting.tasks.daily"
# 	],
# 	"hourly": [
# 		"trigger_contracting.tasks.hourly"
# 	],
# 	"weekly": [
# 		"trigger_contracting.tasks.weekly"
# 	],
# 	"monthly": [
# 		"trigger_contracting.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "trigger_contracting.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "trigger_contracting.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "trigger_contracting.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["trigger_contracting.utils.before_request"]
# after_request = ["trigger_contracting.utils.after_request"]

# Job Events
# ----------
# before_job = ["trigger_contracting.utils.before_job"]
# after_job = ["trigger_contracting.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"trigger_contracting.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

