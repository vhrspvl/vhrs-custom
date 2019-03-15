# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
import time
from frappe.utils.data import today, get_timestamp, formatdate


@frappe.whitelist(allow_guest=True)
def attendance():
    # restrict request from list of IP addresses
    try:
        userid = frappe.form_dict.get("userid")
        employee = frappe.db.get_value("Employee", {
            "employee_no": userid, 'status': 'Active'})
        if employee:
            date = time.strftime("%Y-%m-%d", time.gmtime(
                int(frappe.form_dict.get("att_time"))))
            name, company = frappe.db.get_value(
                "Employee", employee, ["employee_name", "company"])
            attendance_id = frappe.db.get_value("Attendance", {
                "employee": employee, "attendance_date": date})
            is_leave = check_leave_record(employee, date)
            if is_leave == 'On Leave':
                attendance = frappe.new_doc("Attendance")
                in_time = time.strftime("%H:%M:%S", time.gmtime(
                    int(frappe.form_dict.get("att_time"))))
                attendance.update({
                    "employee": employee,
                    "employee_name": name,
                    "attendance_date": date,
                    "status": "On Leave",
                    "in_time": "00:00:00",
                    "out_time": "00:00:00",
                    "company": company
                })
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()
                frappe.response.type = "text"
                return "ok"
            else:
                if attendance_id:
                    attendance = frappe.get_doc("Attendance", attendance_id)
                    out_time = time.strftime("%H:%M:%S", time.gmtime(
                        int(frappe.form_dict.get("att_time"))))
                    if not attendance.in_time:
                        attendance.in_time = out_time
                    else:
                        times = [out_time, attendance.in_time]
                        attendance.out_time = max(times)
                        attendance.in_time = min(times)
                    attendance.db_update()
                    frappe.db.commit()
                    frappe.response.type = "text"
                    return "ok"
                else:
                    attendance = frappe.new_doc("Attendance")
                    in_time = time.strftime("%H:%M:%S", time.gmtime(
                        int(frappe.form_dict.get("att_time"))))
                    attendance.update({
                        "employee": employee,
                        "employee_name": name,
                        "attendance_date": date,
                        "status": "Present",
                        "in_time": in_time,
                        "company": company
                    })
                    attendance.save(ignore_permissions=True)
                    attendance.submit()
                    frappe.db.commit()
                    send_present_alert(employee, name, in_time, date)
                    frappe.response.type = "text"
                    return "ok"
        else:
            employee = frappe.form_dict.get("userid")
            date = time.strftime("%Y-%m-%d", time.gmtime(
                int(frappe.form_dict.get("att_time"))))
            ure_id = frappe.db.get_value("Unregistered Employee", {
                "employee": employee, "attendance_date": date})
            if ure_id:
                attendance = frappe.get_doc(
                    "Unregistered Employee", ure_id)
                out_time = time.strftime("%H:%M:%S", time.gmtime(
                    int(frappe.form_dict.get("att_time"))))
                times = [out_time, attendance.in_time]
                attendance.out_time = max(times)
                attendance.in_time = min(times)
                attendance.db_update()
                frappe.db.commit()
            else:
                attendance = frappe.new_doc("Unregistered Employee")
                in_time = time.strftime("%H:%M:%S", time.gmtime(
                    int(frappe.form_dict.get("att_time"))))
                attendance.update({
                    "employee": employee,
                    "attendance_date": date,
                    "stgid": frappe.form_dict.get("stgid"),
                    "in_time": in_time,
                })
                attendance.save(ignore_permissions=True)
                frappe.db.commit()
            frappe.response.type = "text"
            return "ok"
    except frappe.ValidationError as e:
        log_error("ValidationError", e)
        frappe.response.type = "text"
        return "ok"


def log_error(method, message):
    # employee = message["userid"]
    message = frappe.utils.cstr(message) + "\n" if message else ""
    d = frappe.new_doc("Error Log")
    d.method = method
    d.error = message
    d.insert(ignore_permissions=True)


def check_leave_record(employee, date):
    leave_record = frappe.db.sql("""select leave_type, half_day from `tabLeave Application`
    where employee = %s and %s between from_date and to_date and status = 'Approved'
    and docstatus = 1""", (employee, date), as_dict=True)
    if leave_record:
        if leave_record[0].half_day:
            status = 'Half Day'
        else:
            status = 'On Leave'
            leave_type = leave_record[0].leave_type

        return status


def send_present_alert(employee, name, in_time, date):
    recipients = frappe.get_value("Employee", employee, "user_id")
    frappe.sendmail(
        recipients=recipients,
        subject='IN Punch Alert for ' + formatdate(today()),
        message="""
        <h3> In Punch Alert</h3>
        <p>Dear %s,</p>
        <h4>Info:</h4>
        <p>This is to intimate that today has been marked as Present and your In Time is %s 
        submission of Attendance is subject to your Out Time.</p><br> Regards <br>HR Team
        """ % (name, in_time)
    )
