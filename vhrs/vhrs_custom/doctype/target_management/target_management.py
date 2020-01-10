# -*- coding: utf-8 -*-
# Copyright (c) 2019, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.accounts.utils import get_fiscal_year


class TargetManagement(Document):
    pass


@frappe.whitelist()
def get_target(fiscal_yr, name, division, start_date, end_date, target_type):
    amount = []
    year = frappe.get_doc("Fiscal Year", fiscal_yr)
    # frappe.errprint(year.year_start_date)
    if target_type == "Collection":
        collection = frappe.db.sql(
            """select sum(paid_amount) as amount,month(posting_date) from `tabPayment Entry` where `payment_type`= "Receive" and `posting_date` between %s and %s and `division` = %s group by month(posting_date) """, (year.year_start_date, year.year_end_date, division), as_dict=True)
        for col in collection:
            amount.append(col.amount)
        # frappe.errprint(collection)
        # frappe.errprint(name)
        # frappe.db.set_value("Target Management", name, "annual", collection)
        return amount

    if target_type == "Sales Order":
        sales_order = frappe.db.sql(
            """select sum(base_grand_total) from `tabSales Order` where `transaction_date` between %s and %s and `division` = %s and `order_type` ="Sales" and `docstatus`= 1 """, (start_date, end_date, division))
        # frappe.errprint(sales_order)
        # frappe.errprint(name)
        # frappe.db.set_value("Target Management", name, "annual", sales_order)
