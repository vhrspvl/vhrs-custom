# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils.data import today
from frappe.utils import cint, fmt_money
import requests
from datetime import datetime


@frappe.whitelist()
def get_candidates(customer):
    candidate_list = frappe.get_list("Closure", fields=["name", "passport_no"], filters={
        "customer": customer})
    return candidate_list


@frappe.whitelist()
def add_customer(doc, method):
    customer = frappe.db.get_value("User", {"email": frappe.session.user},
                                   ["customer"])
    doc.customer = customer


@frappe.whitelist()
def mark_absent():
    present_employees = get_employees_who_are_present()
    employees = frappe.get_all('Employee')
    for employee in present_employees:
        if employee in employees:
            print "present"
        else:
            print "absent"


@frappe.whitelist()
def mark_territory():
    projects = frappe.db.sql("""
    select name,customer from tabProject where territory is null
    """, as_dict=1)
    for project in projects:
        customer_territory = frappe.db.get_value(
            "Customer", project["customer"], "territory")
        project = frappe.get_doc("Project", project["name"])
        project.update({
            "territory": customer_territory
            # "services": "Recruitment Service"
        })
        project.flags.ignore_mandatory = True
        project.save(ignore_permissions=True)


def get_employees_who_are_present():
    return frappe.db.sql("""select employee
		from tabAttendance where attendance_date =%(date)s""", {"date": today()}, as_dict=True)

# @frappe.whitelist(allow_guest=True)
# def update_leave_application():
#     employees = frappe.get_all('Employee')
#     for employee in employees:
#         attendance = frappe.db.get_all('Attendance', fields={'employee', 'attendance_date', 'status'}, filters={
#             'attendance_date': today(), 'employee': employee.name})
#         if not attendance:
#             lap = frappe.new_doc("Leave Application")
#             lap.leave_type = "Leave Without Pay"
#             lap.status = "Approved"
#             lap.from_date = today()
#             lap.to_date = today()
#             lap.employee = employee.name
#             lap.leave_approver = "Administrator"
#             lap.posting_date = today()
#             lap.company = frappe.db.get_value(
#                 "Employee", employee.name, "company")
#             lap.save(ignore_permissions=True)
#             lap.submit()
#             frappe.db.commit()

# 0 def temp_so():
#     closures = frappe.db.sql(""" select c.* from tabClosure as c where c.status != 'Onboarded' and
#     c.status != 'Waitlisted' and c.status != 'Sales Order' and c.status != 'PSL'
#     and c.status != 'Dropped' and c.candidate_sc > 0""", as_dict=1)
#     for closure in closures:
#         item_candidate_id = frappe.db.get_value(
#             "Item", {"name": closure.name + "_Candidate"})
#         if item_candidate_id:
#             pass
#         else:
#             if closure.candidate_payment_applicable:
#                 item = frappe.new_doc("Item")
#                 item.standard_rate = closure.candidate_sc
#                 item.payment_type = "Candidate"
#                 item.item_code = closure.name + "_Candidate"
#                 item.item_name = closure.name1
#                 item.item_group = "Recruitment"
#                 item.stock_uom = "Nos"
#                 item.description = closure.customer
#                 item.insert()
#                 item.save(ignore_permissions=True)

#                 so = frappe.new_doc("Sales Order")
#                 so.customer = closure.customer
#                 so.payment_type = "Candidate"
#                 so.append("items", {
#                     "item_code": item.item_code,
#                     "item_name": item.item_name,
#                     "description": item.description,
#                     "uom": item.stock_uom,
#                     "rate": item.standard_rate,
#                     "delivery_date": today()
#                 })
#                 so.insert()
#                 so.submit()
#                 so.save(ignore_permissions=True)

# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

# @frappe.whitelist(allow_guest=True)
# def attendance():
#     global attendance_date, att_time
#     userid = frappe.form_dict.get("userid")
#     employee = frappe.db.get_value("Employee", {
#         "biometric_id": userid})
#     if employee:
#         date = time.strftime("%Y-%m-%d", time.gmtime(
#             int(frappe.form_dict.get("att_time"))))

#         attendance_date = time.strftime("%Y-%m-%d %X", time.gmtime(
#             int(frappe.form_dict.get("att_time"))))

#         doc = frappe.get_doc("Employee", employee)
#         query = """SELECT ro.name, ro.shift FROM `tabRoster` ro, `tabRoster Details` rod
# 		WHERE rod.parent = ro.name AND ro.from_date <= '%s' AND ro.to_date >= '%s'
# 		AND rod.employee = '%s' """ % (attendance_date, attendance_date, doc.employee)
#         roster = frappe.db.sql(query, as_list=1)
#         if len(roster) < 1:
#             attendance_id = frappe.db.get_value("Attendance", {
#                 "employee": employee, "attendance_date": date})
#             if attendance_id:
#                 attendance = frappe.get_doc(
#                     "Attendance", attendance_id)
#                 out_time = time.strftime("%H:%M:%S", time.gmtime(
#                     int(frappe.form_dict.get("att_time"))))
#                 times = [out_time, attendance.in_time]
#                 attendance.out_time = max(times)
#                 attendance.in_time = min(times)
#                 attendance.db_update()
#                 frappe.db.commit()
#             else:
#                 attendance = frappe.new_doc("Attendance")
#                 in_time = time.strftime("%H:%M:%S", time.gmtime(
#                     int(frappe.form_dict.get("att_time"))))
#                 attendance.update({
#                     "employee": employee,
#                     "employee_name": doc.employee_name,
#                     "attendance_date": date,
#                     "status": "Present",
#                     "in_time": in_time,
#                     "company": doc.company
#                 })
#                 attendance.save(ignore_permissions=True)
#                 attendance.submit()
#                 frappe.db.commit()
#             frappe.response.type = "text"
#             return "ok"
#         else:
#             doc.shift = roster[0][1]

#             shft = frappe.get_doc("Shift Details", doc.shift)
#             att_date = datetime.strptime(
#                 attendance_date, '%Y-%m-%d %H:%M:%S')

#             if shft.in_out_required:
#                 shft_hrs = shft.hours_required_per_day.seconds

#                 shft_indate = datetime.combine(att_date, datetime.min.time())
#                 shft_intime = shft_indate + timedelta(0, shft.in_time.seconds)
#                 shft_intime_max = shft_intime + \
#                     timedelta(0, shft.delayed_entry_allowed_time.seconds)
#                 shft_intime_min = shft_intime - \
#                     timedelta(0, shft.early_entry_allowed_time.seconds)

#                 attendance_id = frappe.db.get_value("Attendance", {
#                     "employee": employee, "attendance_date": date})
#                 if attendance_id:
#                     attendance = frappe.get_doc(
#                         "Attendance", attendance_id)
#                     out_time = time.strftime("%H:%M:%S", time.gmtime(
#                         int(frappe.form_dict.get("att_time"))))
#                     times = [out_time, attendance.in_time]
#                     attendance.out_time = max(times)
#                     attendance.in_time = min(times)
#                     total_hrs = time_diff_in_seconds(
#                         attendance.out_time, attendance.in_time)
#                     attendance.overtime = (total_hrs - shft_hrs) / 3600
#                     attendance.db_update()
#                     frappe.db.commit()
#                 else:
#                     if att_date >= shft_intime_min and att_date <= shft_intime_max:
#                         attendance = frappe.new_doc(
#                             "Attendance")
#                         intime = time.strftime("%H:%M:%S", time.gmtime(
#                             int(frappe.form_dict.get("att_time"))))
#                         attendance.update({
#                             "employee": employee,
#                             "employee_name": doc.employee_name,
#                             "attendance_date": shft_indate,
#                             "status": "Present",
#                             "in_time": intime,
#                             "company": doc.company
#                         })
#                         attendance.save(
#                             ignore_permissions=True)
#                         attendance.submit()
#                         frappe.db.commit()
#                     else:
#                         attendance = frappe.new_doc(
#                             "Attendance")
#                         intime = time.strftime("%H:%M:%S", time.gmtime(
#                             int(frappe.form_dict.get("att_time"))))
#                         attendance.update({
#                             "employee": employee,
#                             "employee_name": doc.employee_name,
#                             "attendance_date": shft_indate,
#                             "status": "Absent",
#                             "in_time": intime,
#                             "company": doc.company
#                         })
#                         attendance.save(
#                             ignore_permissions=True)
#                         frappe.db.commit()
#                 frappe.response.type = "text"
#                 return "ok"

# @frappe.whitelist(allow_guest=True)
# def attendance():
#     global attendance_date, att_time
#     userid = frappe.form_dict.get("userid")
#     employee = frappe.db.get_value("Employee", {
#         "biometric_id": userid})
#     if employee:
#         date = time.strftime("%Y-%m-%d", time.gmtime(
#             int(frappe.form_dict.get("att_time"))))

#         attendance_date = time.strftime("%Y-%m-%d %X", time.gmtime(
#             int(frappe.form_dict.get("att_time"))))

#         doc = frappe.get_doc("Employee", employee)
#         query = """SELECT ro.name, ro.shift FROM `tabRoster` ro, `tabRoster Details` rod
# 		WHERE rod.parent = ro.name AND ro.from_date <= '%s' AND ro.to_date >= '%s'
# 		AND rod.employee = '%s' """ % (attendance_date, attendance_date, doc.employee)
#         roster = frappe.db.sql(query, as_list=1)
#         if len(roster) < 1:
#             attendance_id = frappe.db.get_value("Attendance", {
#                 "employee": employee, "attendance_date": date})
#             if attendance_id:
#                 attendance = frappe.get_doc(
#                     "Attendance", attendance_id)
#                 out_time = time.strftime("%H:%M:%S", time.gmtime(
#                     int(frappe.form_dict.get("att_time"))))
#                 times = [out_time, attendance.in_time]
#                 attendance.out_time = max(times)
#                 attendance.in_time = min(times)
#                 attendance.db_update()
#             else:
#                 attendance = frappe.new_doc("Attendance")
#                 in_time = time.strftime("%H:%M:%S", time.gmtime(
#                     int(frappe.form_dict.get("att_time"))))
#                 attendance.update({
#                     "employee": employee,
#                     "employee_name": doc.employee_name,
#                     "attendance_date": date,
#                     "status": "Present",
#                     "in_time": in_time,
#                     "company": doc.company
#                 })
#                 attendance.save(ignore_permissions=True)
#                 attendance.submit()
#                 frappe.db.commit()
#             frappe.response.type = "text"
#             return "ok"
#         else:
#             doc.shift = roster[0][1]

#             shft = frappe.get_doc("Shift Details", doc.shift)
#             att_date = datetime.strptime(
#                 attendance_date, '%Y-%m-%d %H:%M:%S')

#             if shft.in_out_required:
#                 shft_indate = datetime.combine(att_date, datetime.min.time())
#                 shft_intime = shft_indate + timedelta(0, shft.in_time.seconds)
#                 shft_intime_max = shft_intime + \
#                     timedelta(0, shft.delayed_entry_allowed_time.seconds)
#                 shft_intime_min = shft_intime - \
#                     timedelta(0, shft.early_entry_allowed_time.seconds)

#                 attendance_id = frappe.db.get_value("Attendance", {
#                     "employee": employee, "attendance_date": date})
#                 if attendance_id:
#                     attendance = frappe.get_doc(
#                         "Attendance", attendance_id)
#                     out_time = time.strftime("%H:%M:%S", time.gmtime(
#                         int(frappe.form_dict.get("att_time"))))
#                     times = [out_time, attendance.in_time]
#                     attendance.out_time = max(times)
#                     attendance.in_time = min(times)
#                     attendance.db_update()
#                 else:
#                     if att_date >= shft_intime_min and att_date <= shft_intime_max:
#                         attendance = frappe.new_doc(
#                             "Attendance")
#                         intime = time.strftime("%Y-%m-%d %X", time.gmtime(
#                             int(frappe.form_dict.get("att_time"))))
#                         attendance.update({
#                             "employee": employee,
#                             "employee_name": doc.employee_name,
#                             "attendance_date": shft_indate,
#                             "status": "Present",
#                             "in_time": intime,
#                             "company": doc.company
#                         })
#                         attendance.save(
#                             ignore_permissions=True)
#                         attendance.submit()
#                         frappe.db.commit()
#                     else:
#                         attendance = frappe.new_doc(
#                             "Attendance")
#                         intime = time.strftime("%Y-%m-%d %X", time.gmtime(
#                             int(frappe.form_dict.get("att_time"))))
#                         attendance.update({
#                             "employee": employee,
#                             "employee_name": doc.employee_name,
#                             "attendance_date": shft_indate,
#                             "status": "Absent",
#                             "in_time": intime,
#                             "company": doc.company
#                         })
#                         attendance.save(
#                             ignore_permissions=True)
#                 frappe.response.type = "text"
#                 return "ok"


@frappe.whitelist()
def update_in_biometric_machine(uid, uname):
    stgids = frappe.db.get_all("Service Tag")
    # stgid = 'ST-KY18000181'
    for stgid in stgids:
        url = "http://robot.camsunit.com/external/1.0/user/update?uid=%s&uname=%s&stgid=%s" % (
            uid, uname, stgid.name)
        r = requests.post(url)
    frappe.errprint(r.content)
    return r.content


@frappe.whitelist()
def rename_si(doc, method):
    for item in doc.items:
        item_name = item.item_code
    payment_type = frappe.db.get_value(
        "Sales Order Item", {'item_code': item_name}, "payment_type")
    if payment_type == 'Candidate':
        new_name = doc.name + "/" + item_name
        # if doc.name != new_name and not doc.is_new():
        #     frappe.rename_doc(doc.doctype,doc.name,new_name)


@frappe.whitelist()
def create_sales_order(name, customer, project, name1, passport_no, candidate_sc, client_sc, is_client, is_candidate):
    # if 'Project Leader' in frappe.get_roles(frappe.session.user):
    #     if doc.sales_order_confirmed_date:
    #         pass
    #     else:
    territory = frappe.db.get_value("Customer", customer, "territory")
    if is_candidate or is_client:
        frappe.errprint(is_candidate)
        frappe.errprint(is_client)
        item_candidate_id = frappe.db.get_value(
            "Item", {"name": name + "_Candidate"})
        item_pp_id = frappe.db.get_value(
            "Item", {"name": passport_no})
        if item_candidate_id or item_pp_id:
            pass
        else:
            item = frappe.new_doc("Item")
            if territory == 'India':
                item.item_code = name
            else:
                item.item_code = passport_no
            item.item_name = name1
            item.item_group = "Recruitment"
            item.stock_uom = "Nos"
            item.description = customer
            item.insert()
            item.save(ignore_permissions=True)

            if is_candidate == '1':
                frappe.errprint(is_candidate)
                so = frappe.new_doc("Sales Order")
                so.customer = customer
                so.project = project
                so.payment_type = "Candidate"
                so.passport_no = passport_no,
                so.territory = territory
                so.append("items", {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "payment_type": "Candidate",
                    "description": item.description,
                    "uom": item.stock_uom,
                    "rate": candidate_sc,
                    "delivery_date": today()
                })
                so.insert()
                so.submit()
                so.save(ignore_permissions=True)

            if is_client == '1':
                so = frappe.new_doc("Sales Order")
                so.customer = customer
                so.project = project
                so.payment_type = "Client"
                so.passport_no = passport_no
                so.territory = territory
                so.append("items", {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "payment_type": "Client",
                    "description": item.description,
                    "uom": item.stock_uom,
                    "rate": client_sc,
                    "delivery_date": today()
                })
                so.insert()
                so.submit()
                so.save(ignore_permissions=True)
            total = cint(candidate_sc) + cint(client_sc)

            return "Sales Order Created for Total value {0}".format(frappe.bold(fmt_money(total, currency='INR')))
        # closure = frappe.get_doc("Closure", doc)
        # closure.csl_status = 'Sales Order Confirmed'
        # closure.sales_order_confirmed_date = today()
        # closure.save(ignore_permissions=True)


def update_status(doc, method):
    projects = frappe.get_all('Project', fields={'name', 'status'})
    for project in projects:
        tasks = frappe.db.get_all('Task', fields={'name', 'project', 'status'}, filters={
            'project': project.name})
        if tasks:
            if any(task.status == 'Open' or task.status == 'Working' or task.status == 'Pending Review' or task.status == 'Overdue' for task in tasks):
                frappe.db.set_value(
                    "Project", project.name, "status", "Open")
            elif all(task.status == 'Cancelled' for task in tasks):
                frappe.db.set_value(
                    "Project", project.name, "status", "Cancelled")
            elif all(task.status == 'DnD' for task in tasks):
                frappe.db.set_value(
                    "Project", project.name, "status", "Completed")

    customers = frappe.get_all('Customer', fields={'name', 'status'})
    for customer in customers:
        projects = frappe.db.get_all('Project', fields={'name', 'customer', 'status'}, filters={
            'customer': customer.name})
        if projects:
            if all(project.status == 'Open' or project.status == 'Overdue' or project.status == 'DnD' for project in projects):
                frappe.db.set_value(
                    "Customer", customer.name, "status", "Open")
            else:
                frappe.db.set_value(
                    "Customer", customer.name, "status", "Active")


def punch_record():
    from zk import ZK, const
    conn = None
    zk = ZK('192.168.1.65', port=4370, timeout=5)
    try:
        conn = zk.connect()
        attendance = conn.get_attendance()
        curdate = datetime.now().date()
        for att in attendance:
            # if att.user_id == '170':
            date = att.timestamp.date()
            if date == curdate:
                mtime = att.timestamp.time()
                userid = att.user_id
                employee = frappe.db.get_value("Employee", {
                    "employee_no": userid, "status": "Active"})
                if employee:
                    doc = frappe.get_doc("Employee", employee)
                    pr_id = frappe.db.get_value("Punch Record", {
                        "employee": employee, "attendance_date": date})
                if pr_id:
                    pr = frappe.get_doc("Punch Record", pr_id)
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
