
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
# app_include_js = "/assets/vhrs/js/qrcode.min.js"
# app_include_js = "/assets/vhrs/js/vhrs.js"
# on_login = "vhrs.custom.daily_quote"
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
        # "validate": "vhrs.custom.mark_territory",
        "validate": "vhrs.custom.update_task_operation_Status"
    },
    # "Closure": {
    #     "on_update": "vhrs.custom.so_from_import"
    # }
    # "Performance Management Self":
    # {
    #     "on_submit": "vhrs.custom.update_pm_manager"
    # },
    # "Performance Management Manager":
    # {
    #     "on_submit": "vhrs.custom.update_pm_reviewer"
    # },

    # "Attendance": {
    #     "validate": "vhrs.custom.validatetime"
    # }
    # "Attendance Log": {
    #     "on_update": "vhrs.utility.post_att"
    # }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    # 	"all": [
    # 		"vhrs.tasks.all"
    # 	],
    # 	"hourly": [
    # 		"vhrs.tasks.hourly"
    # 	],
    "weekly": [
        # "vhrs.tasks.weekly",
        "vhrs.email_alerts.closure_drop_alert"
    ],
    "daily": [
        "vhrs.custom.send_active_report",
        "vhrs.permission.mark_comp_off_new",
        "vhrs.custom.update_holiday_attendance",
        "vhrs.custom.update_status",
        "vhrs.custom.update_last_sync",
        "vhrs.custom.make_ibd",
        "vhrs.custom.mark_punch_time"
        # "vhrs.custom.update_task_status"
        # "vhrs.permission.update_drafts",

    ],
    "monthly": [
        # "vhrs.tasks.monthly"
        "vhrs.email_alerts.speciallist",
        "vhrs.permission.mark_cl",
        # "vhrs.custom.update_pm_basic"
    ],
    # "cron": {
    #     "45 07 * * *": [
    #         "vhrs.permission.mark_absent_a"
    #     ],
    #     "00 09 * * *": [
    #         # "vhrs.email_alerts.send_preday_report",
    #         # "vhrs.permission.update_autopresent"
    #     ],
    #     "16 09 * * *": [
    #         # "vhrs.permission.mark_absent_g"
    #     ],
    #     "50 09 * * *": [
    #         # "vhrs.permission.update_att_a"
    #     ],
    #     "07 11 * * *": [
    #         # "vhrs.permission.update_att_g"
    #     ],
    #     "15 11 * * *": [
    #         # "vhrs.custom.punch_record",
    #         # "vhrs.email_alerts.send_daily_report",
    #         # "vhrs.email_alerts.absent_list_alert"
    #     ],
    #     "0 11-23/1 * * *": [
    #         "vhrs.permission.mark_hd"
    #     ],
    #     "15 0 */2 * * ": [
    #         "vhrs.permission.mark_att"
    #     ],
    #     "50 23 * * *": [
    #         "vhrs.permission.total_working_hours",
    #         "vhrs.permission.half_day"
    #     ],
    #     "55 23 * * *": [
    #         # "vhrs.email_alerts.send_absent_alert",
    #         # "vhrs.email_alerts.send_failed_punch_alert"
    #         "vhrs.permission.update_attendance"
    #     ],
    # }

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
