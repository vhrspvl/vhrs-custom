
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "vhrs"
app_title = "VHRS Custom"
app_publisher = "VHRS"
app_description = "Custom doctypes of VHRS"
app_icon = "octicon octicon-gear"
app_color = "grey"
app_email = "erp@voltechgroup.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/vhrs/css/vhrs.css"
# app_include_js = "/assets/vhrs/js/vhrs.js"

# include js, css files in header of web template
# web_include_css = "/assets/vhrs/css/vhrs.css"
# web_include_js = "/assets/vhrs/js/vhrs.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "vhrs.utils.get_home_page"
fixtures = ["Custom Field", "Custom Script", "Property Setter"]
# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "vhrs.install.before_install"
# after_install = "vhrs.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "vhrs.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Project": {
        "validate": "vhrs.custom.mark_territory"
    },
    # "Attendance": {
    #     "validate": "vhrs.custom.validatetime"
    # }
    # "Project": {
    #     "on_update": "vhrs.utils.update_status"
    # }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    # 	"all": [
    # 		"vhrs.tasks.all"
    # 	],
    "daily": [
        "vhrs.utils.update_status"
    ],
    "cron": {
        "00 10 * * *": [
            "vhrs.custom.punch_record",
            "vhrs.custom.send_daily_report"
        ]
    }
    # 	"hourly": [
    # 		"vhrs.tasks.hourly"
    # 	],
    # 	"weekly": [
    # 		"vhrs.tasks.weekly"
    # 	]
    # 	"monthly": [
    # 		"vhrs.tasks.monthly"
    # 	]
}

# Testing
# -------

# before_tests = "vhrs.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "vhrs.event.get_events"
# }
