# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe.utils.data import today
from frappe.utils import cstr, formatdate, add_months, cint, fmt_money, add_days, flt
import requests
from datetime import datetime, timedelta, date
from frappe import throw, _, scrub
import time


@frappe.whitelist(allow_guest=True)
def attendance():
    # restrict request from list of IP addresses
    try:
        userid = frappe.form_dict.get("userid")
        employee = frappe.db.get_value("Employee", {
            "employee_no": userid, 'status': 'Active'})
        if employee:
            log_error("Att Type", frappe.form_dict.get("att_type"))
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


@frappe.whitelist()
def punch_record(curdate):
    from zk import ZK, const
    conn = None
    zk = ZK('192.168.1.65', port=4370, timeout=5)
    try:
        conn = zk.connect()
        attendance = conn.get_attendance()
        # curdate = datetime.now().date()
        # curdate = '2019-04-03'
        for att in attendance:
            # if att.user_id == '170':
            date = att.timestamp.date()
            if date == curdate:
                mtime = att.timestamp.time()
                mtimef = timedelta(
                    hours=mtime.hour, minutes=mtime.minute, seconds=mtime.second)
                userid = att.user_id
                employee = frappe.db.get_value("Employee", {
                    "employee_no": userid, "status": "Active"})
                if employee:
                    doc = frappe.get_doc("Employee", employee)
                    already_exist = False
                    pr_id = frappe.db.get_value("Punch Record", {
                        "employee": employee, "attendance_date": date})
                    if pr_id:
                        pr = frappe.get_doc("Punch Record", pr_id)
                        # max(i.punchtime)
                        for i in pr.timetable:
                            if i.punch_time == mtimef:
                                already_exist = True
                        if not already_exist:
                            pr.append("timetable", {
                                "punch_time": str(mtime)
                            })
                            pr.save(ignore_permissions=True)
                    else:
                        pr = frappe.new_doc("Punch Record")
                        pr.employee = employee
                        pr.employee_name = doc.employee_name
                        pr.attendance_date = date
                        pr.append("timetable", {
                            "punch_time": mtime
                        })
                        pr.insert()
                        pr.save(ignore_permissions=True)
    except Exception, e:
        print "Process terminate : {}".format(e)
    finally:
        if conn:
            conn.disconnect()


@frappe.whitelist()
def mark_attendance(day):
    # day = datetime.strptime('2019-07-15', "%Y-%m-%d").date()
    # day = '2019-07-03'
    # in_time = out_time = ""
    # employees = ['24']
    employees = frappe.get_all(
        "Employee", {"status": "Active", "employment_type": ("!=", "Contract")})
    for emp in employees:
        # print emp.name
        emp = emp.name
        doj = frappe.get_value("Employee", emp, "date_of_joining")
        shift = frappe.get_value("Employee", emp, "shift")
        wh_for_halfday = timedelta(hours=5)
        wh_for_fullday = timedelta(hours=9, minutes=30)
        if shift:
            wh_for_halfday = frappe.get_value(
                "Shift", shift, ["wh_for_halfday"])
            wh_for_fullday = frappe.get_value(
                "Shift", shift, ["wh_for_fullday"])
        # frappe.errprint(doj)
        # frappe.errprint(day)
        if doj <= day:
            times = []
            twh = ""
            status = 'Absent'
            punch_record = frappe.db.exists(
                "Punch Record", {"attendance_date": day, "employee": emp})
            if punch_record:
                pr = frappe.get_doc("Punch Record", punch_record)
                # frappe.errprint(pr.employee_name)
                # frappe.errprint(pr.attendance_date)
                working_shift = frappe.db.get_value(
                    "Employee", {'employee': emp}, ['shift'])
                for t in pr.timetable:
                    times.append(t.punch_time)
                in_time = min(times)
                out_time = max(times)
                if in_time == out_time:
                    out_time = ""
                att_id = frappe.get_value(
                    "Attendance", {"attendance_date": day, "employee": emp})
                if att_id:
                    if in_time and out_time:
                        twh = out_time - in_time

                        if twh > wh_for_halfday:
                            status = 'Half Day'
                        if twh >= wh_for_fullday:
                            status = 'Present'
                    # if not punch_record and att_id['in_time'] and att_id['out_time']:
                    #     in_time = in_time
                    #     out_time = out_time

                    att = frappe.get_doc("Attendance", att_id)
                    att.update({
                        "in_time": in_time,
                        "out_time": out_time,
                        "total_working_hours": twh,
                        "status": status
                    })
                    if att.docstatus == 1:
                        att.db_update()
                        frappe.db.commit()
                    else:
                        att.save(ignore_permissions=True)
                        att.submit()
                        frappe.db.commit()
                else:
                    att = frappe.new_doc("Attendance")
                    att.update({
                        "employee": emp,
                        "employment_type": frappe.get_value("Employee", emp, "employment_type"),
                        "attendance_date": day,
                        "shift": working_shift,
                        "status": status,
                        # "in_time": in_time,
                    })
                    att.save(ignore_permissions=True)
                    frappe.db.commit()


@frappe.whitelist()
def fetch_from_ui(from_date, to_date, fetch_type):
    from_date = (datetime.strptime(str(from_date), '%Y-%m-%d')).date()
    to_date = (datetime.strptime(str(to_date), '%Y-%m-%d')).date()
    for preday in daterange(from_date, to_date):
        if fetch_type == "att":
            mark_attendance(preday)
        else:
            punch_record(preday)


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n)
