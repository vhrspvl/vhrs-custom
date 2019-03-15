# -*- coding: utf-8 -*-
# Copyright (c) 2018, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
from frappe import _
from frappe.utils import comma_or, today, flt, add_days, date_diff, getdate


# class InvalidApproverError(frappe.ValidationError):
#     pass


# class LeaveApproverIdentityError(frappe.ValidationError):
#     pass


class AttendancePermission(Document):
    pass
#     def on_submit(self):
#         if self.status == "Open":
#             frappe.throw(
# _("Only Applications with status 'Approved' and 'Rejected' can be
# submitted"))

#     def validate(self):
#         self.validate_approver()

#     def validate_approver(self):
#         employee = frappe.get_doc("Employee", self.employee)
#         approvers = [l.leave_approver for l in employee.get("leave_approvers")]

#         if len(approvers) and self.approver not in approvers:
#             frappe.throw(_("Approver must be one of {0}")
#                          .format(comma_or(approvers)), InvalidApproverError)

#         elif self.approver and not frappe.db.sql("""select name from `tabHas Role`
#             where parent=%s and role='Leave Approver'""", self.approver):
#             frappe.throw(_("{0} ({1}) must have role 'Approver'")
#                          .format(get_fullname(self.approver), self.approver), InvalidApproverError)

#         elif self.docstatus == 0 and len(approvers) and self.approver != frappe.session.user:
#             self.status = 'Open'

#         elif self.docstatus == 1 and len(approvers) and self.approver != frappe.session.user:
#             frappe.throw(_("Only the selected Approver can submit this Application"),
#                          LeaveApproverIdentityError)


# @frappe.whitelist()
# def update_att(doc, method):
#     if type(doc.from_time) is datetime:
#         from_date = doc.from_time.date()
#     else:
#         from_date = datetime.strptime(
#             doc.from_time, '%Y-%m-%d %H:%M:%S').date()
#     if doc.status == "Approved":
#         if frappe.get_value('Attendance', {"employee": doc.employee, "attendance_date": from_date}):
#             attendance = frappe.get_doc(
#                 'Attendance', {"employee": doc.employee, "attendance_date": from_date})
#             if attendance:
#                 attendance.update({
#                     "permission_in_time": doc.from_time,
#                     "permission_out_time": doc.to_time,
#                     "total_hour": doc.total_hours,
#                     "explanation": doc.explanation
#                 })
#                 attendance.db_update()
#                 frappe.db.commit()
