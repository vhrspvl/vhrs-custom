# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


@frappe.whitelist()
def add_customer(doc, method):
    customer = frappe.db.get_value("User", {"email": frappe.session.user},
                                   ["customer"])
    doc.customer = customer


# def update_status():
#     projects = frappe.get_all('Project', fields={'name', 'status'})
#     for project in projects:
#         tasks = frappe.db.get_all('Task', fields={'name', 'project', 'status'}, filters={
#             'project': project.name})
#         if tasks:
#             if all(task.status == 'Closed' or task.status == 'Completed' for task in tasks):
#                 frappe.db.set_value(
#                     "Project", project.name, "status", "Completed")
#             elif all(task.status == 'Cancelled' for task in tasks):
#                 frappe.db.set_value(
#                     "Project", project.name, "status", "Cancelled")
#             else:
#                 frappe.db.set_value(
#                     "Project", project.name, "status", "Open")

#     customers = frappe.get_all('Customer', fields={'name', 'status'})
#     for customer in customers:
#         projects = frappe.db.get_all('Project', fields={'name', 'customer', 'status'}, filters={
#             'customer': customer.name})
#         if projects:
#             if all(project.status == 'Open' for project in projects):
#                 frappe.db.set_value(
#                     "Customer", customer.name, "status", "Open")
#             else:
#                 frappe.db.set_value(
#                     "Customer", customer.name, "status", "Active")
