# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.utils import flt
from frappe import _
import frappe


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_employees(filters)

    return columns, data


def get_columns():
    return [
        _("Employee") + ":Link/Employee:120", _("Name") +
        ":Data:200", _("Date of Joining") + ":Date:100",
        _("Branch") + ":Link/Branch:120", _("Department") + ":Link/Department:120",
        _("Designation") + ":Link/Designation:120", _("Gender") +
        "::60", _("Company") + ":Link/Company:120"
    ]


def get_employees(filters):
    conditions = get_conditions(filters)
    return frappe.db.sql("""select name, employee_name, date_of_joining,
	branch, department, designation,
	gender, company from tabEmployee where status = 'Active' %s""" % conditions, as_list=1)


def get_conditions(filters):
    conditions = ""
    if filters.get("month"):
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
                 "Dec"].index(filters["month"]) + 1
        conditions += " and month(date_of_joining) = '%s'" % month

    if filters.get("company"):
        conditions += " and company = '%s'" % \
            filters["company"].replace("'", "\\'")

    return conditions
