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
    columns = get_columns()
    conditions, filters = get_conditions(filters)
    attendance = get_attendance(conditions, filters)
    late = " "
    for att in attendance:
        working_shift = frappe.db.get_value(
            "Employee", {'employee': att.employee}, ['shift'])
        shift_time = frappe.db.get_value("Shift", {'name': working_shift})
        dt = datetime.strftime(att.attendance_date, "%d-%m-%y")
        if working_shift == 'G':
            if att.in_time:
                in_t = datetime.strptime(
                    att.in_time, '%H:%M:%S').time()
                in_time = timedelta(
                    hours=in_t.hour, minutes=in_t.minute, seconds=in_t.second).total_seconds()
                shift_in_time = timedelta(
                    hours=9, minutes=15, seconds=0).total_seconds()
                late = in_time - shift_in_time
                t_g = timedelta(seconds=late)

        elif working_shift == 'A':
            if att.in_time:
                in_t = datetime.strptime(
                    att.in_time, '%H:%M:%S').time()
                in_time = timedelta(
                    hours=in_t.hour, minutes=in_t.minute, seconds=in_t.second).total_seconds()
                shift_in_time = timedelta(
                    hours=7, minutes=15, seconds=0).total_seconds()
                late = in_time - shift_in_time
                t_a = timedelta(seconds=late)
            # frappe.errprint(att.employee)
        if late > float(0):
            if att.in_time:
                if att.employee:
                    row = [att.employee]
                else:
                    row = ["-"]
                if att.employee_name:
                    row += [att.employee_name]
                else:
                    row += ["-"]
                if att.business_unit:
                    row += [att.business_unit]
                else:
                    row += ["-"]
                if att.attendance_date:
                    row += [dt]
                else:
                    row += ["-"]
                if att.in_time:
                    row += [att.in_time]
                else:
                    row += ["-"]
                if att.out_time:
                    row += [att.out_time]
                else:
                    row += ["-"]
                if working_shift == 'G':
                    row += [str(t_g)]
                else:
                    row += ["-"]
                if working_shift == 'A':
                    row += [str(t_a)]
                else:
                    row += ["-"]
                data.append(row)
    return columns, data


def get_employees(filters):
    conditions = get_conditions(filters)
    query = """SELECT employee,employee_name, business_unit FROM `tabEmployee` WHERE status='Active' and company = "Voltech HR Services Private Limited" and employment_type != "Contract" and branch != "Nepal" and branch != "UAE" %s
        ORDER BY employee""" % conditions
    data = frappe.db.sql(query, as_dict=1)
    return data


def get_first_day(dt, d_years=0, d_months=0):
    # d_years, d_months are "deltas" to apply to dt
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m - 1, 12)
    return date(y + a, m + 1, 1)


def get_last_day(dt):
    return get_first_day(dt, 0, 1) + timedelta(-1)


def get_columns():
    columns = [_("Employee Code") + ":Data:100", _("Name") + ":Data:150", _("Business_unit") + ":Data:100", _("Date") + ":Data:100",
               _("In Time") + ":Data:100", _("Out Time") + ":Data:100", _("Late-In") + ":Data:100"]

    # for day in range(filters["total_days_in_month"]):
    #     columns.append(cstr(day + 1) + "::20")

    return columns


def get_attendance(conditions, filters):
    attendance = frappe.db.sql("""
    select
    att.leave_type,att.name as name,att.attendance_date as attendance_date,att.employee as employee, att.employee_name as employee_name,emp.employment_type as employment_type,att.business_unit as business_unit,att.in_time as in_time,att.out_time as out_time
    from `tabAttendance` att
    left join `tabEmployee` emp on att.employee = emp.employee
    where
    att.docstatus != 2
     %s
    order by att.attendance_date""" % conditions, filters, as_dict=1)
    return attendance


def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += "and att.attendance_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " and att.attendance_date <= %(to_date)s"

    if filters.get("employee"):
        conditions += "AND att.employee = '%s'" % filters["employee"]
    return conditions, filters
