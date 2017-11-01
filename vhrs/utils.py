# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils.data import today


@frappe.whitelist()
def add_customer(doc, method):
    customer = frappe.db.get_value("User", {"email": frappe.session.user},
                                   ["customer"])
    doc.customer = customer


def update_status(doc, method):
    projects = frappe.get_all('Project', fields={'name', 'status'})
    for project in projects:
        tasks = frappe.db.get_all('Task', fields={'name', 'project', 'status'}, filters={
            'project': project.name})
        if tasks:
            if any(task.status == 'Open' or task.status == 'Working' or task.status == 'Pending Review' or task.status == 'Overdue' for task in tasks):
                frappe.db.set_value(
                    "Project", project.name, "status", "Open")
                frappe.errprint('hi')
            elif all(task.status == 'Cancelled' for task in tasks):
                frappe.db.set_value(
                    "Project", project.name, "status", "Cancelled")
                frappe.errprint('hii')
            elif all(task.status == 'DnD' for task in tasks):
                frappe.db.set_value(
                    "Project", project.name, "status", "Completed")
                frappe.errprint('hiii')

    customers = frappe.get_all('Customer', fields={'name', 'status'})
    for customer in customers:
        projects = frappe.db.get_all('Project', fields={'name', 'customer', 'status'}, filters={
            'customer': customer.name})
        if projects:
            if all(project.status == 'Open' for project in projects):
                frappe.db.set_value(
                    "Customer", customer.name, "status", "Open")
            else:
                frappe.db.set_value(
                    "Customer", customer.name, "status", "Active")


@frappe.whitelist(allow_guest=True)
def attendance(**args):
    userid = frappe.form_dict.get("userid")
    attendance_id = frappe.db.get_value("Attendance", {
        "employee": userid, "attendance_date": today()})
    if attendance_id:
        attendance = frappe.get_doc("Attendance", attendance_id)
    else:
        name, company = frappe.db.get_value(
            "Employee", userid, ["employee_name", "company"])
        attendance = frappe.new_doc("Attendance")
        attendance.employee = userid
        attendance.employee_name = name
        attendance.attendance_date = today()
        attendance.status = "Present"
        attendance.company = company
        attendance.submit()
        frappe.db.commit()
    return 'ok'
