# -*- coding: utf-8 -*-
# Copyright (c) 2019, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, formatdate, add_months, cint, fmt_money, add_days, flt, get_first_day, get_last_day


class PerformanceManagement(Document):
    def autoname(self):
        self.name = self.employee_code+"-"+self.month

    def on_submit(self):
        if self.grade:
            emp = frappe.get_doc("Employee", self.employee_code)
            emp.update({
                "pm_grade": self.grade,
                "pm_generated_date": self.date_of_rating
            })
            emp.save(ignore_permissions=True)
            frappe.db.commit()


@frappe.whitelist()
def auto_generate_kra(kra_type, pm_date, executive):
    first_day = get_first_day(pm_date)
    last_day = get_last_day(pm_date)
    if kra_type == "Closure":
        closure_list = frappe.db.sql("""select * from `tabClosure` where csl_status= "Sales Order Confirmed" and sales_order_confirmed_date between '%s' and '%s' and 
        source_executive = '%s' """ % (first_day, last_day, executive), as_dict=1)
        if len(closure_list) == 0:
            return "Empty"
        else:
            return len(closure_list)
    if kra_type == "Lead":
        lead_list = frappe.db.sql("""select * from `tabLead` where status= "Converted" and last_called_date between '%s' and '%s' and 
        lead_owner = '%s' and lead_potential="A+ - Very High"  """ % (first_day, last_day, executive), as_dict=1)
        if len(lead_list) == 0:
            return "Empty"
        else:
            return len(lead_list)
    if kra_type == "CandidatePSL":
        candidate_list = frappe.db.sql("""select * from `tabCandidate` where pending_for="Proposed PSL" and interview_date between '%s' and '%s' and 
        user='%s'  """ % (first_day, last_day, executive), as_dict=1)
        frappe.errprint(candidate_list)
        if len(candidate_list) == 0:
            return "Empty"
        else:
            return len(candidate_list)
    # if kra_type == "CollectionDnD":
    #     candidate_list = frappe.db.sql("""select * from `tabClosure` where candidate_payment_applicable=1 and interview_date between '%s' and '%s' and
    #     lead_owner = '%s' and user='%s'  """ % (first_day, last_day, executive), as_dict=1)
    #     if len(candidate_list) == 0:
    #         return "Empty"
    #     else:
    #         return candidate_list
    if kra_type == "Opportunity":
        candidate_list = frappe.db.sql("""select * from `tabLead` where status= "Opportunity" and last_called_date between '%s' and '%s' and 
        lead_owner = '%s'  """ % (first_day, last_day, executive), as_dict=1)
        if len(candidate_list) == 0:
            return "Empty"
        else:
            return len(candidate_list)
