# -*- coding: utf-8 -*-
# Copyright (c) 2018, VHRS and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
from frappe import _
from frappe.utils import today, flt, add_days, date_diff, getdate, cint, formatdate, getdate, get_link_to_form, \
    comma_or, get_fullname


class InvalidApproverError(frappe.ValidationError):
    pass


class LeaveApproverIdentityError(frappe.ValidationError):
    pass


class OverlapError(frappe.ValidationError):
    pass


class OnDutyApplication(Document):
    def on_submit(self):
        if self.status == "Open":
            frappe.throw(
                _("Only Applications with status 'Approved' and 'Rejected' can be submitted"))
        elif self.status == "Approved":
            request_days = date_diff(self.to_date, self.from_date) + 1
            for number in range(request_days):
                attendance_date = add_days(self.from_date, number)
                skip_attendance = validate_if_attendance_not_applicable(
                    self.employee, attendance_date)
                if not skip_attendance:
                    att = frappe.db.exists(
                        "Attendance", {"employee": self.employee, "attendance_date": attendance_date})
                    if att:
                        attendance = frappe.get_doc("Attendance", att)
                        attendance.update({
                            "status": "Present",
                            "onduty_status": "On Duty"
                            # "on_duty_application": doc.name
                        })
                        attendance.db_update()
                        frappe.db.commit()
                    else:
                        attendance = frappe.new_doc("Attendance")
                        attendance.employee = self.employee
                        attendance.employee_name = self.employee_name
                        attendance.status = "Present"
                        attendance.attendance_date = attendance_date
                        attendance.in_time = ""
                        attendance.out_time = ""
                        attendance.onduty_status = "On Duty"
                        attendance.company = self.company
                        attendance.save(ignore_permissions=True)
                        attendance.submit()

#         if self.status == "Approved":
#             day = datetime.strptime(add_days(today(), -1), "%Y-%m-%d").date()

#             from_date = add_days(day, -1)
#             to_date = add_months(day, 12)
#             diff = date_diff()

#             if self.from_date <= self.to_date:
#                 holiday_list = frappe.db.get_value(
#                     "Employee", {'employee': self.employee}, ['holiday_list'])
#                 holiday_date = frappe.db.get_value(
#                     "Holiday", {'holiday_date': day,
#                                 'parent': holiday_list}, ["holiday_date"]
#                 )
#                 if self.half_day == 0:
#                     new_leaves_allocated = 0.5
#                 if self.half_day == 1:
#                     new_leaves_allocated = 1
#                 lal_ids = frappe.get_doc("Leave Allocation", self.employee)
#                 if lal_ids:
#                     lal.new_leaves_allocated += new_leaves_allocated
#                     lal.total_leaves_allocated += new_leaves_allocated
#                     if lal.description:
#                         lal.description += '<br>' + \
#                             'Comp-off for {0}'.format(day)
#                     else:
#                         lal.description = '<br>' + \
#                             'Comp-off for {0}'.format(day)
#                     lal.db_update()
#                     frappe.db.commit
#                 else:
#                     lal = frappe.new_doc("Leave Allocation")
#                     lal.employee = od.employee
#                     lal.leave_type = 'Compensatory Off'
#                     lal.from_date = day
#                     lal.to_date = to_date
#                     lal.new_leaves_allocated = new_leaves_allocated
#                     lal.description = 'Comp-off for {0}'.format(day)
#                     lal.save(ignore_permissions=True)
#                     lal.submit()
#                     frappe.db.commit()


# def get_lal(emp, day):
#     lal = frappe.db.sql("""select name from `tabLeave Allocation`
#                 where employee = %s and %s between from_date and to_date and leave_type='Compensatory Off'
#             and docstatus = 1""", (emp, day), as_dict=True)
#     return lal

#     # od_ids = frappe.get_list('On Duty Application', {"docstatus" : 2})
    # for od in od_ids:
    #     if od:
    #         datetime.strptime(add_days(tdatetime.strptime(add_days(today(),-1), "%Y-%m-%d").date()oday(),-1), "%Y-%m-%d").date()
    #         new_leaves_allocated = 0
    #         att = frappe.get_doc("Attendance", att_id)


    def validate(self):
        self.validate_approver()
        self.validate_od_overlap()

    def validate_approver(self):
        employee = frappe.get_doc("Employee", self.employee)
        approvers = [l.leave_approver for l in employee.get("leave_approvers")]

        if len(approvers) and self.approver not in approvers:
            frappe.throw(_("Approver must be one of {0}")
                         .format(comma_or(approvers)), InvalidApproverError)

        elif self.approver and not frappe.db.sql("""select name from `tabHas Role`
            where parent=%s and role='Leave Approver'""", self.approver):
            frappe.throw(_("{0} ({1}) must have role 'Approver'")
                         .format(get_fullname(self.approver), self.approver), InvalidApproverError)

        elif self.docstatus == 0 and len(approvers) and self.approver != frappe.session.user:
            self.status = 'Open'

        elif self.docstatus == 1 and len(approvers) and self.approver != frappe.session.user:
            frappe.throw(_("Only the selected Approver can submit this Application"),
                         LeaveApproverIdentityError)

    def validate_od_overlap(self):
        if not self.name:
            # hack! if name is null, it could cause problems with !=
            self.name = "New On Duty Application"

        for d in frappe.db.sql("""
                select
                    name, on_duty_type, posting_date, from_date, to_date, total_number_of_days, half_day_date
                from `tabOn Duty Application`
                where employee = %(employee)s and docstatus < 2 and status in ("Open","Approved")
                and to_date >= %(from_date)s and from_date <= %(to_date)s
                and name != %(name)s""", {
            "employee": self.employee,
            "from_date": self.from_date,
            "to_date": self.to_date,
            "name": self.name
        }, as_dict=1):

            if cint(self.half_day) == 1 and getdate(self.half_day_date) == getdate(d.half_day_date) and (
                    flt(self.total_leave_days) == 0.5
                    or getdate(self.from_date) == getdate(d.to_date)
                    or getdate(self.to_date) == getdate(d.from_date)):

                total_leaves_on_half_day = self.get_total_leaves_on_half_day()
                if total_leaves_on_half_day >= 1:
                    self.throw_overlap_error(d)
            else:
                self.throw_overlap_error(d)

    def throw_overlap_error(self, d):
        msg = _("Employee {0} has already applied for {1} between {2} and {3}").format(self.employee,
                                                                                       d['on_duty_type'], formatdate(d['from_date']), formatdate(d['to_date'])) \
            + """ <br><b><a href="#Form/On Duty Application/{0}">{0}</a></b>""".format(d["name"])
        frappe.throw(msg, OverlapError)

    # def on_cancel(self):
    #     attendance_list = frappe.get_list(
    #         "Attendance", {'employee': self.employee, 'on_duty_application': self.name})
    #     if attendance_list:
    #         for attendance in attendance_list:
    #             attendance_obj = frappe.get_doc(
    #                 "Attendance", attendance['name'])
    #             attendance_obj.cancel()


# @frappe.whitelist()
# def on_duty_mark(doc, method):
#     if doc.status == "Approved":
#         request_days = date_diff(doc.to_date, doc.from_date) + 1
#         for number in range(request_days):
#             attendance_date = add_days(doc.from_date, number)
#             skip_attendance = validate_if_attendance_not_applicable(
#                 doc.employee, attendance_date)
#             if not skip_attendance:
#                 att = frappe.db.exists(
#                     "Attendance", {"employee": doc.employee, "attendance_date": attendance_date})
#                 if att:
#                     attendance = frappe.get_doc("Attendance", att)
#                     attendance.update({
#                         "status": "Present",
#                         "onduty_status": "On Duty"
#                         # "on_duty_application": doc.name
#                     })
#                     attendance.db_update()
#                     frappe.db.commit()
#                 else:
#                     attendance = frappe.new_doc("Attendance")
#                     attendance.employee = doc.employee
#                     attendance.employee_name = doc.employee_name
#                     attendance.status = "Present"
#                     attendance.attendance_date = attendance_date
#                     attendance.in_time = ""
#                     attendance.out_time = ""
#                     attendance.onduty_status = "On Duty"
#                     attendance.company = doc.company
#                     attendance.save(ignore_permissions=True)
#                     attendance.submit()


def validate_if_attendance_not_applicable(employee, attendance_date):
    # Check if attendance_date is a Holiday
    if is_holiday(employee, attendance_date):
        frappe.msgprint(_("Attendance not submitted for {0} as it is a Holiday.").format(
            attendance_date), alert=1)
        return True
    # Check if employee on Leave
    leave_record = frappe.db.sql("""select half_day from `tabLeave Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1""", (employee, attendance_date), as_dict=True)
    if leave_record:
        frappe.msgprint(_("Attendance not submitted for {0} as {1} on leave.").format(
            attendance_date, employee), alert=1)
        return True

    return False


def get_holiday_list_for_employee(employee, raise_exception=True):
    if employee:
        holiday_list, company = frappe.db.get_value(
            "Employee", employee, ["holiday_list", "company"])
    else:
        holiday_list = ''
        company = frappe.db.get_value(
            "Global Defaults", None, "default_company")

    if not holiday_list:
        holiday_list = frappe.get_cached_value(
            'Company',  company,  "default_holiday_list")

    if not holiday_list and raise_exception:
        frappe.throw(_('Please set a default Holiday List for Employee {0} or Company {1}').format(
            employee, company))

    return holiday_list


def is_holiday(employee, date=None):
    '''Returns True if given Employee has an holiday on the given date
    :param employee: Employee `name`
    :param date: Date to check. Will check for today if None'''

    holiday_list = get_holiday_list_for_employee(employee)
    if not date:
        date = today()

    if holiday_list:
        return frappe.get_all('Holiday List', dict(name=holiday_list, holiday_date=date)) and True or False


@frappe.whitelist()
def get_number_of_leave_days(employee, from_date, to_date, half_day=None, half_day_date=None):
    number_of_days = 0
    if cint(half_day) == 1:
        if from_date == to_date:
            number_of_days = 0.5
        else:
            number_of_days = date_diff(to_date, from_date) + .5
    else:
        number_of_days = date_diff(to_date, from_date) + 1

    return number_of_days
