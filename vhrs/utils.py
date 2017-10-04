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


def addecode(doc, method):
    doc.employee_no = make_autoname("V.####")
