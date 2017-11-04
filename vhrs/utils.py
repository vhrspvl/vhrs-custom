# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils.data import today
from frappe.utils.response import as_text


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
            if all(project.status == 'Open' or project.status == 'Overdue' project.status == 'DnD' for project in projects):
                frappe.db.set_value(
                    "Customer", customer.name, "status", "Open")
            else:
                frappe.db.set_value(
                    "Customer", customer.name, "status", "Active")


@frappe.whitelist(allow_guest=True)
def attendance():
    if frappe.local.request.remote_addr not in ["192.168.1.65", "127.0.0.1"]: # restrict request from list of IP addresses
		raise (frappe.exceptions.PermissionError)
    else:    
        userid = frappe.form_dict.get("userid")
        employee = frappe.db.get_value("Employee", {
            "employee_no": userid})
        attendance_id = frappe.db.get_value("Attendance", {
            "employee": employee, "attendance_date": today()})
        if attendance_id:
            attendance = frappe.get_doc("Attendance",attendance_id)
            attendance.out_time = frappe.form_dict.get("att_time")
        else:
            name, company = frappe.db.get_value(
                "Employee", employee, ["employee_name", "company"])
            attendance = frappe.new_doc("Attendance")
            attendance.employee = employee
            attendance.employee_name = name
            attendance.attendance_date = today()
            attendance.status = "Present"
            attendance.in_time = frappe.form_dict.get("att_time")
            attendance.company = company
            attendance.insert(ignore_permissions=True)
            attendance.submit()
            frappe.db.commit()
    frappe.response.type = "text"
    return "ok"