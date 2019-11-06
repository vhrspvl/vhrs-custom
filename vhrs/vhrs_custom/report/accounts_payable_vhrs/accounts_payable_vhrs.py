# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from vhrs.vhrs_custom.report.accounts_receivable_vhrs.accounts_receivable_vhrs import ReceivablePayableReport


def execute(filters=None):
    args = {
        "party_type": "Supplier",
        "naming_by": ["Buying Settings", "supp_master_name"],
    }
    return ReceivablePayableReport(filters).run(args)
