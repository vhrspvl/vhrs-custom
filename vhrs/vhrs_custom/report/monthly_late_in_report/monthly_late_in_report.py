# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals
import frappe
from frappe import _
import math
from calendar import monthrange
from datetime import datetime, timedelta, date
from dateutil.rrule import *
from frappe.utils import getdate, cint, add_months, date_diff, add_days, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds, today


def execute(filters=None):
    if not filters:
        filters = {}
    data = row = []
    filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
                        "Dec"].index(filters.month) + 1
    columns = [_("Employee Code") + ":Data:150", _("Name") + ":Data:150", _("Designation") + ":Data:150",
               _("Permission Counts") + ":Data:150", _("Permission Days") + ":Data:300"]

    # month = filters.month - 1
    # year = filters.year
    # if month == 0:
    #     month = 12
    #     year = cint(filters.year) - 1
    # frappe.errprint(cint(filters.year))
    # frappe.errprint(month)
    # frappe.errprint(filters.year)
    # tdm = monthrange(cint(filters.year), month)[1]
    day = date.today()
    start_date = get_first_day(day)
    end_date = get_last_day(day)
    # frappe.errprint(start_date)
    for emp in get_employees(filters):
        d = []
        row = [emp.employee, emp.employee_name, emp.designation]
        permission = frappe.db.sql(
            """select permission_date from `tabAttendance Permission` Where employee = %s and permission_date between %s and %s and company ="Voltech HR Services Private Limited" """, (emp.employee, start_date, end_date))
        # frappe.errprint(permission)
        for p in permission:
            # frappe.errprint(emp.employee)
            # frappe.errprint(p[1])
            if p:

                d.append(p[0].strftime("%d"))

        # frappe.errprint(emp.employee)
        # frappe.errprint(d)
        # c = ','.join(d)
        row += [len(d), d]
        data.append(row)
    return columns, data


def get_employees(filters):
    conditions = get_conditions(filters)
    query = """SELECT employee,employee_name,designation, business_unit FROM `tabEmployee` WHERE status='Active' and company = "Voltech HR Services Private Limited" and employment_type != "Contract"  %s
        ORDER BY employee""" % conditions
    data = frappe.db.sql(query, as_dict=1)
    return data


def get_conditions(filters):
    conditions = ""

    if filters.get("employee"):
        conditions += "AND employee = '%s'" % filters["employee"]

    if filters.get("business_unit"):
        conditions += " AND business_unit = '%s'" % filters["business_unit"]

    return conditions


def get_first_day(dt, d_years=0, d_months=0):
    # d_years, d_months are "deltas" to apply to dt
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m - 1, 12)
    return date(y + a, m + 1, 1)


def get_last_day(dt):
    return get_first_day(dt, 0, 1) + timedelta(-1)
