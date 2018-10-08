# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
import socket,os
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils.data import today
from frappe.utils import formatdate, cint, fmt_money, add_days
import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
import time
# from netifaces import netifaces


@frappe.whitelist(allow_guest=True)
def bioupdate():
    # restrict request from list of IP addresses
    userid = frappe.form_dict.get("uid")
    bu = frappe.new_doc("Biometric Update")
    if userid:
        bu.uid = userid
    else:
        bu.uid = "hi"
    bu.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.response.type = "text"
    return "ok"


@frappe.whitelist()
def send_drop_list():
    from_date = str(date.today() - relativedelta(weeks=1))
    to_date = add_days(today(), -1)
    # print type(from_date)
    custom_filter = {'from_date': from_date, 'to_date': to_date}
    report = frappe.get_doc('Report', "Dropped Candidate List")
    columns, data = report.get_data(
        limit=500 or 500, filters=custom_filter, as_dict=True)
    html = frappe.render_template(
        'frappe/templates/includes/print_table.html', {'columns': columns, 'data': data})
    msg = "Kindly find the attached Dropped Candidate List Dated From " + \
        formatdate(from_date) + " To " + formatdate(to_date)
    frappe.sendmail(
        recipients=['prabavathi.d@voltechgroup.com'],
        subject='Dropped Candidate List Upto - ' +
        formatdate(add_days(today(), -1)),
        message=msg + html
    )


@frappe.whitelist()
def send_dropped_list():
    from_date = str(date.today() - relativedelta(months=1))
    to_date = add_days(today(), -1)
    # print type(from_date)
    custom_filter = {'from_date': from_date, 'to_date': to_date}
    report = frappe.get_doc('Report', "Dropped Candidate List")
    columns, data = report.get_data(
        limit=500 or 500, filters=custom_filter, as_dict=True)
    html = frappe.render_template(
        'frappe/templates/includes/print_table.html', {'columns': columns, 'data': data})
    msg = "Kindly find the attached Dropped Candidate List Dated From " + \
        formatdate(from_date) + " To " + formatdate(to_date)
    frappe.sendmail(
        recipients=['prabavathi.d@voltechgroup.com'],
        subject='Dropped Candidate List Upto - ' +
        formatdate(add_days(today(), -1)),
        message=msg + html
    )


# @frappe.whitelist()
# def send_drop_report():
#     report = frappe.get_doc('Report', "Dropped Candidate List")
#     columns, data = report.get_data(
#         limit=500 or 500, as_dict=True)
#     html = frappe.render_template(
#         'frappe/templates/includes/print_table.html', {'columns': columns, 'data': data})
#     frappe.sendmail(
#         recipients=['Prabavathi.d@voltechgroup.com'],
#         subject = 'Dropped Candidate List ' +
#         message=html
#     )

@frappe.whitelist()
def get_candidates(customer):
    candidate_list=frappe.get_list("Closure", fields = ["name", "passport_no"], filters = {
        "customer": customer})
    return candidate_list


@frappe.whitelist()
def add_customer(doc, method):
    customer=frappe.db.get_value("User", {"email": frappe.session.user},
                                   ["customer"])
    doc.customer=customer


@frappe.whitelist()
def markic():
    all_so=frappe.get_all("Sales Order", fields = ['name', 'territory'])
    for so in all_so:
        sales_order=frappe.get_doc("Sales Order", so["name"])
        if so['territory'] == 'India':
            sales_order.hrsic='BUHR-III'
            sales_order.flags.ignore_mandatory=True
            sales_order.save(ignore_permissions = True)
            frappe.db.commit()


@frappe.whitelist()
def bulk_mark_dnd_incharge():
    closures=frappe.db.sql("""
    select name,project from tabClosure where dnd_incharge is null
    """, as_dict = 1)
    for closure in closures:
        dnd_incharge=frappe.db.get_value(
            "Project", closure["project"], "dnd_incharge")
        if dnd_incharge:
            closure = frappe.get_doc("Closure", closure["name"])
            closure.dnd_incharge = dnd_incharge
            closure.db_update()


@frappe.whitelist()
def bulk_mark_territory():
    tasks = frappe.db.sql("""
    select name,project from `tabTask` where territory is null""", as_dict=1)
    for t in tasks:
        territory = frappe.db.get_value(
            "Project", t["project"], "territory")

        if territory:
            task = frappe.get_doc("Task", t["name"])
            task.territory = territory
            task.db_update()


@frappe.whitelist()
def mark_territory(doc, method):
    customer_territory = frappe.db.get_value(
        "Customer", doc.customer, "territory")
    doc.territory = customer_territory


@frappe.whitelist()
def mark_project_type():
    mark_project = frappe.db.sql("""
        select name from tabProject
            """, as_dict=1)
    for project in mark_project:
        project_type = frappe.db.set_value(
            "Project", project.name, "project_type", "External")
        department = frappe.db.set_value(
            "Project", project.name, "department", "REC")
        if project_type:
            project = frappe.get_doc("Project", project["name"])
            project.project_type = project_type
            project.db_update()
            frappe.db.commit()
        if department:
            project = frappe.get_doc("Project", project["name"])
            project.department = department
            project.db_update()
            frappe.db.commit()


@frappe.whitelist()
def mark_task_dept():
    mark_task = frappe.db.sql("""
        select name from tabTask
            """, as_dict=1)
    for task in mark_task:
        department = frappe.db.set_value(
            "Task", task.name, "department", "REC")
        if department:
            task = frappe.get_doc("Task", task["name"])
            task.department = department
            task.db_update()
            frappe.db.commit()


@frappe.whitelist()
def delete_bulk():
    left_employees = frappe.get_list(
        "Employee", fields=["employee_no", "name"], filters={"status": "Left", "is_deleted": 0})
    print len(left_employees)
    # for l in left_employees:
    #     stgids = frappe.db.get_all("Service Tag")
    #     for stgid in stgids:
    #         uid = l.employee_no
    #         url = "http://robot.camsunit.com/external/1.0/user/delete?uid=%s&stgid=%s" % (
    #             uid, stgid.name)
    #         r = requests.post(url)
    #         if r.content == "OK":
    #             emp = frappe.get_doc("Employee", l.name)
    #             emp.is_deleted = 1
    #             emp.db_update()
    #             frappe.db.commit()
    #             return r.content


# # @frappe.whitelist()
# def mark_dnd_incharge(doc,method):


def get_employees_who_are_present():
    return frappe.db.sql("""select employee
        from tabAttendance where attendance_date =%(date)s""", {"date": today()}, as_dict=True)


def temp_so():
    closures = frappe.db.sql(
        """select c.* from tabClosure as c where c.sales_order_confirmed_date <= '2018-01-19' and
        c.status !='Dropped' and c.status != 'Waitlisted' and c.status != 'Sales Order' and c.status != 'PSL' and not c.sales_order_confirmed_date is null
        """, as_dict=1)
    for closure in closures:
        # print closure.name, closure.sales_order_confirmed_date
        territory = frappe.db.get_value(
            "Customer", closure.customer, "territory")
        item_candidate_id = frappe.db.get_value(
            "Item", {"name": closure.name + "_Candidate"})
        item_name_id = frappe.db.get_value(
            "Item", {"name": closure.name})
        item_pp_id = frappe.db.get_value(
            "Item", {"name": closure.passport_no})
        if item_candidate_id or item_pp_id or item_name_id:
            print 'passed'
            pass
        else:
            item = frappe.new_doc("Item")
            if territory == 'India':
                item.item_code = closure.name
            else:
                if closure.passport_no:
                    item.item_code = closure.passport_no
                else:
                    item.item_code = closure.name
                item.item_name = closure.name1
                item.item_group = "Recruitment"
                item.stock_uom = "Nos"
                item.description = closure.customer
                item.insert()
                item.save(ignore_permissions=True)
                frappe.db.commit()
                print 'item inserted', item.item_name, item.item_code

            if closure.candidate_payment_applicable:
                if closure.candidate_sc > 0:
                    so = frappe.new_doc("Sales Order")
                    so.customer = closure.customer
                    so.project = closure.project
                    so.payment_type = "Candidate"
                    so.passport_no = closure.passport_no,
                    so.territory = territory
                    so.append("items", {
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "payment_type": "Candidate",
                        "description": item.description,
                        "uom": item.stock_uom,
                        "rate": closure.candidate_sc,
                        "delivery_date": '2017-12-31'
                    })
                    so.insert()
                    so.submit()
                    so.save(ignore_permissions=True)
                    frappe.db.commit()
                    print 'cand_so', so.name

            if closure.client_payment_applicable:
                if closure.client_sc > 0:
                    so = frappe.new_doc("Sales Order")
                    so.customer = closure.customer
                    so.project = closure.project
                    so.payment_type = "Client"
                    so.passport_no = closure.passport_no
                    so.territory = territory
                    so.append("items", {
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "payment_type": "Client",
                        "description": item.description,
                        "uom": item.stock_uom,
                        "rate": closure.client_sc,
                        "delivery_date": '2017-12-31'
                    })
                    so.insert()
                    so.submit()
                    so.save(ignore_permissions=True)
                    frappe.db.commit()
                    print 'client_so', so.name


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
def create_sales_order(name, customer, project, name1, passport_no, candidate_sc, client_sc, is_client, is_candidate):
    territory = frappe.db.get_value("Customer", customer, "territory")
    cg = frappe.db.get_value("Customer", customer, "customer_group")
    if is_candidate or is_client:
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
                so = frappe.new_doc("Sales Order")
                so.customer = customer
                so.project = project
                so.payment_type = "Candidate"
                so.passport_no = passport_no,
                so.territory = territory
                so.customer_group = cg
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
                so.customer_group = cg
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


@frappe.whitelist()
def recreate_sales_order(name, customer, project, name1, passport_no, redeputation_cost):
    territory = frappe.db.get_value("Customer", customer, "territory")
    cg = frappe.db.get_value("Customer", customer, "customer_group")
    if redeputation_cost:
        item_candidate_id = frappe.db.get_value(
            "Item", {"name": passport_no + "_Redeputed"})
        if item_candidate_id:
            pass
        else:
            item = frappe.new_doc("Item")
            item.item_code = passport_no + "_Redeputed"
            item.item_name = name1
            item.item_group = "Recruitment"
            item.stock_uom = "Nos"
            item.description = customer + "_Redeputed"
            item.insert()
            item.save(ignore_permissions=True)

            if redeputation_cost:
                so = frappe.new_doc("Sales Order")
                so.customer = customer
                so.project = project
                so.payment_type = "Client"
                so.passport_no = passport_no,
                so.territory = territory
                so.customer_group = cg
                so.append("items", {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "payment_type": "Client",
                    "description": item.description,
                    "uom": item.stock_uom,
                    "rate": redeputation_cost,
                    "delivery_date": today()
                })
                so.insert()
                so.submit()
                so.save(ignore_permissions=True)

            return "Sales Order Created for Total value {0}".format(frappe.bold(fmt_money(redeputation_cost, currency='INR')))


def update_status():
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


@frappe.whitelist(allow_guest=True)
def get_zk():
    frappe.response.type = "text"
    return "ok"


@frappe.whitelist()
def send_daily_report():
    custom_filter = {'date': today()}
    report = frappe.get_doc('Report', "Employee Day Attendance")
    columns, data = report.get_data(
        limit=500 or 500, filters=custom_filter, as_dict=True)
    html = frappe.render_template(
        'frappe/templates/includes/print_table.html', {'columns': columns, 'data': data})
    frappe.sendmail(
        recipients=['prabavathi.d@voltechgroup.com',
                    'dineshbabu.k@voltechgroup.com',
                    'sangeetha.a@voltechgroup.com',
                    'sangeetha.s@voltechgroup.com',
                    'jagan.k@voltechgroup.com',
                    'dhavachelvan.d@voltechgroup.com',
                    'selvaraj.g@voltechgroup.com',
                    'mohanraj.e@voltechgroup.com'
                    ],
        subject='Employee Attendance Report - ' +
        formatdate(today()),
        message=html
    )


@frappe.whitelist()
def send_active_report():
    custom_filter = {'status': "Active",
                     'employment_type': ["not in", ["Contract"]]}
    report = frappe.get_doc('Report', "Active Employees - VHRS")
    columns, data = report.get_data(
        limit=500 or 500, filters=custom_filter, as_dict=True)
    html = frappe.render_template(
        'frappe/templates/includes/print_table.html', {'columns': columns, 'data': data})
    frappe.sendmail(
        recipients=['abdulla.pi@voltechgroup.com',
                    'k.senthilkumar@voltechgroup.com',
                    'dineshbabu.k@voltechgroup.com',
                    'Karthikeyan.n@voltechgroup.com',
                    'Prabavathi.d@voltechgroup.com'

                    ],
        subject='VHRS Active Employees - ',
        message=html
    )


@frappe.whitelist()
def punch_record():
    from zk import ZK, const
    conn = None
    zk = ZK('192.168.1.65', port=4370, timeout=5)
    try:
        conn = zk.connect()
        attendance = conn.get_attendance()
        curdate = datetime.now().date()
        # curdate = '2018-04-12'
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
                        print min(pr.timetable)
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


@frappe.whitelist(allow_guest=True)
def client_feedback():
    first = frappe.form_dict.get("formID")
    last = frappe.form_dict.get("last")
    cf = frappe.new_doc("Client Feedback")
    cf.first_name = first
    cf.last_name = last
    cf.insert()
    cf.save(ignore_permissions=True)


@frappe.whitelist()
def capture_fp(name):
    jsondata = {'Quality': '', 'Timeout': ''}
    # frappe.errprint(active_url)
    r = requests.post(
        'http://10.81.234.7:8004/mfs100/capture', data=jsondata)
    status = r.json()
    if 'IsoTemplate' in status:
        return status['IsoTemplate'], status['BitmapData']


@frappe.whitelist()
def verify_fp(fp):
    # bio_ips = frappe.get_list("Biometric IP")
    # conn = False
    # for bio in bio_ips:
    #     import socket
    #     from urllib2 import urlopen, URLError, HTTPError
    #     socket.setdefaulttimeout(23)  # timeout in seconds
    #     url = 'http://' + bio['name'] + ':8004'
    #     frappe.errprint(url)
    #     try:
    #         response = urlopen(url)
    #     except HTTPError, e:
    #         frappe.errprint(
    #             'The server couldn\'t fulfill the request. Reason: %s' % str(e.code))
    #     except URLError, e:
    #         frappe.errprint(
    #             'We failed to reach a server. Reason:%s' % str(e.reason))
    #     else:
    #         html = response.read()
    #         active_url = url
    #         conn = True
    # if conn:
    active_url = 'http://galfar.pagekite.me'
    frappe.errprint(active_url)
    jsondata = {'BioType': 'FMR', 'GalleryTemplate': fp}
    r = requests.post(active_url + '/mfs100/match', data=jsondata)
    status = r.json()
    frappe.errprint(status)
    if not status['ErrorCode'] == '-1307':
        if 'Status' in status:
            return 'Verified'
        else:
            return 'Not Verified'
    else:
        return 'MFS 100 Not Found'

# def create_journal_entry(self, je_payment_amount, user_remark):
#     	default_payroll_payable_account = self.get_default_payroll_payable_account()
# 		precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

# 		journal_entry = frappe.new_doc('Journal Entry')
# 		journal_entry.voucher_type = 'Bank Entry'
# 		journal_entry.user_remark = _('Payment of {0} from {1} to {2}')\
# 			.format(user_remark, self.start_date, self.end_date)
# 		journal_entry.company = self.company
# 		journal_entry.posting_date = self.posting_date

# 		payment_amount = flt(je_payment_amount, precision)

# 		journal_entry.set("accounts", [
# 			{
# 				"account": self.payment_account,
# 				"credit_in_account_currency": payment_amount
# 			},
# 			{
# 				"account": default_payroll_payable_account,
# 				"debit_in_account_currency": payment_amount,
# 				"reference_type": self.doctype,
# 				"reference_name": self.name
# 			}
# 		])
# 		journal_entry.save(ignore_permissions = True)


        