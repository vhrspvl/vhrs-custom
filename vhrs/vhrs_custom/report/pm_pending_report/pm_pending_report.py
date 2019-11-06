# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime
from frappe import _
from frappe.utils import cint
from calendar import monthrange


def execute(filters=None):
    if not filters:
        filters = {}
    data = row = []
    manager = ""
    columns = get_columns()
    for emp in get_employees(filters):
        row = [emp.employee_code, emp.employee_name, emp.operations_manager,
               emp.unit_head, emp.department, emp.designation]
        if emp.pending == "Self":
            row += ["Pending", "Pending", "Pending"]
        elif emp.pending == "Operations Manager":
            row += ["Completed", "Pending", "Pending"]
        elif emp.pending == "Unit Head":
            row += ["Completed", "Completed", "Pending"]
        elif emp.pending == "Unit Head Completed":
            row += ["Completed", "Completed", "Completed"]
        data.append(row)
    return columns, data


def get_columns():
    columns = [
        _("Employee") + ":Link/Employee:80",
        _("Employee Name") + ":Data:150",
        _("Manager") + ":Data:200",
        _("Reviewer") + ":Data:200",
        _("Department") + ":Link/Department:130",
        _("Designation") + ":Link/Designation:130",
        _("Self Status") + ":Data:100",
        _("Manager Status") + ":Data:100",
        _("Reviewer Status") + ":Data:100",
    ]
    return columns


def get_employees(filters):
    conditions = get_conditions(filters)
    query = """SELECT 
         employee_code ,department,pending,designation,date_of_rating,employee_name,operations_manager,unit_head FROM `tabPerformance Management` where %s
        ORDER BY employee_code""" % conditions
    data = frappe.db.sql(query, as_dict=1)
    return data


def get_conditions(filters):
    conditions = ""

    filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
                        "Dec"].index(filters.month) + 1

    # filters["date_of_rating"] = monthrange(
    #     cint(filters.year), filters.month)[1]
    if filters.get("month"):
        conditions += " month(date_of_rating) = %s " % filters["month"]

    if filters.get("year"):
        conditions += " AND year(date_of_rating) = %s " % filters["year"]

    if filters.get("employee_code"):
        conditions += "AND employee_code = '%s'" % filters["employee_code"]

    if filters.get("department"):
        conditions += " AND department = '%s'" % filters["department"]

    if filters.get("business_unit"):
        conditions += " AND business_unit = '%s'" % filters["business_unit"]

    return conditions
