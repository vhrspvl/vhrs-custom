# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import calendar
import random
import frappe
import socket
import os
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils.data import today
from frappe.utils import formatdate, add_months, cint, fmt_money, add_days
import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from frappe import throw, _, scrub
import time
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
# from netifaces import netifaces

# @frappe.whitelist()
# def daily_quote():
#     quote = """var d = new frappe.ui.Dialog({
#             title: __("Thought of the Day"),
#             'fields': [
#                 {'fieldname': 'ht', 'fieldtype': 'HTML'},
#                 ],
#                 });
#                 d.fields_dict.ht.$wrapper.html('<div style="width:550px;height:300px;"><iframe width="100%" height="100%" src="http://api.wpquoteoftheday.com/widget/1" frameborder="0" ></iframe></div>');
#                 d.show();"""
#     frappe.publish_realtime(event='eval_js',message=quote,user= frappe.session.user)


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
    candidate_list = frappe.get_list("Closure", fields=["name", "passport_no"], filters={
        "customer": customer})
    return candidate_list


@frappe.whitelist()
def add_customer(doc, method):
    customer = frappe.db.get_value("User", {"email": frappe.session.user},
                                   ["customer"])
    doc.customer = customer


@frappe.whitelist()
def markic():
    all_so = frappe.get_all("Sales Order", fields=['name', 'territory'])
    for so in all_so:
        sales_order = frappe.get_doc("Sales Order", so["name"])
        if so['territory'] == 'India':
            sales_order.hrsic = 'BUHR-III'
            sales_order.flags.ignore_mandatory = True
            sales_order.save(ignore_permissions=True)
            frappe.db.commit()


@frappe.whitelist()
def bulk_mark_dnd_incharge():
    closures = frappe.db.sql("""
    select name,project from tabClosure where dnd_incharge is Null
    """, as_dict=1)
    for closure in closures:
        dnd_incharge = frappe.db.get_value(
            "Project", closure["project"], "dnd_incharge")
        if dnd_incharge:
            closure = frappe.get_doc("Closure", closure["name"])
            closure.dnd_incharge = dnd_incharge
            closure.db_update()


@frappe.whitelist()
def update_buhr():
    closures = frappe.db.sql("""
    select * from `tabClosure` """, as_dict=1)
    for closure in closures:
        if closure:
            piv = frappe.get_doc("Closure", closure["name"])
            # print piv
            piv.update({
                "source_executive": piv.dle,
                "cr_executive": piv.cpc,
                "ca_executive": piv.bde,
            })
            piv.db_update()
            frappe.db.commit()


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
def bulk_update_att():
    att = frappe.db.sql("""
    select * from `tabAttendance` """, as_dict=1)
    for at in att:
        branch = frappe.db.get_value(
            "Employee", at["employee"], "branch")
        shift = frappe.db.get_value(
            "Employee", at["employee"], "shift")
        if branch and shift:
            attendance = frappe.get_doc("Attendance", at["name"])
            attendance.branch = branch,
            attendance.shift = shift
            attendance.db_update()


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
def so_territory():
    sales_order = frappe.db.sql("""
    select name,customer from `tabSales Order` where territory = 'All Territories' """, as_dict=1)
    for so in sales_order:
        territory = frappe.db.get_value(
            "Customer", so.customer, "territory")
        if territory:
            sales_order = frappe.get_doc("Sales Order", so["name"])
            sales_order.territory = territory
            sales_order.db_update()


@frappe.whitelist()
def projects_buhr():
    projects = frappe.db.sql("""
    select name,cpc from `tabProject` where business_unit is null""", as_dict=1)
    for project in projects:
        business_unit = frappe.db.get_value(
            "Employee", {'user_id': project.cpc}, ["business_unit"])
        if business_unit:
            project = frappe.get_doc("Project", project["name"])
            project.business_unit = business_unit
            project.db_update()


@frappe.whitelist()
def so_buhr():
    so = frappe.db.sql("""
    select * from `tabSales Order` where ca_executive is null""", as_dict=1)
    for s in so:
        ca_executive = frappe.db.get_value(
            "Closure", {'passport_no': s.passport_no}, ["ca_executive"])
        if ca_executive:
            so = frappe.get_doc("Sales Order", s["name"])
            so.ca_executive = ca_executive
            so.db_update()


@frappe.whitelist()
def random():
    for x in range(10):
        x = random.randint(1, 101)
        return x


@frappe.whitelist()
def grand_amount():
    pi = frappe.db.sql("""
    select * from `tabPurchase Invoice`""", as_dict=1)
    for p in pi:
        if p:
            piv = frappe.get_doc("Purchase Invoice", p["name"])
            # print piv
            piv.update({
                "advance_amount": piv.total_advance
            })
            piv.db_update()
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
    # print len(left_employees)
    for l in left_employees:
        stgids = frappe.db.get_all("Service Tag")
        for stgid in stgids:
            uid = l.employee_no
            url = "http://robot.camsunit.com/external/1.0/user/delete?uid=%s&stgid=%s" % (
                uid, stgid.name)
            r = requests.post(url)
            if r.content == "OK":
                emp = frappe.get_doc("Employee", l.name)
                emp.is_deleted = 1
                emp.db_update()
                frappe.db.commit()


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
def delete_from_biometric_machine(uid, uname):
    stgids = frappe.db.get_all("Service Tag")
    for stgid in stgids:
        url = "http://robot.camsunit.com/external/1.0/user/delete?uid=%s&stgid=%s" % (
            uid, stgid.name)
        r = requests.post(url)
    return r.content

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
def create_sales_order(name, customer, project, name1, passport_no, client_sc, candidate_sc, business_unit, source_executive, ca_executive, is_candidate, is_client):
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
                so.passport_no = passport_no
                so.territory = territory
                so.passport_no = passport_no
                # so.business_unit = business_unit
                # so.source_executive = source_executive
                # so.ca_executive = ca_executive
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
                # so.business_unit = business_unit
                # so.source_executive = source_executive
                # so.ca_executive = ca_executive
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
def send_active_report():
    custom_filter = {'status': "Active",
                     'employment_type': ["not in", ["Contract"]]}
    report = frappe.get_doc('Report', "Active Employees - VHRS")
    columns, data = report.get_data(
        limit=500 or 500, filters=custom_filter, as_dict=True)
    html = frappe.render_template(
        'frappe/templates/includes/print_table.html', {'columns': columns, 'data': data})
    frappe.sendmail(
        recipients=['k.senthilkumar@voltechgroup.com',
                    'dineshbabu.k@voltechgroup.com',
                    'Karthikeyan.n@voltechgroup.com',
                    'Prabavathi.d@voltechgroup.com'
                    ],
        subject='VHRS Active Employees - ',
        message=html
    )
    # frappe.errprint(html)


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


@frappe.whitelist()
def mark_comment():
    # l = frappe.get_doc("Lead",lead)
    frappe.errprint("hi")
    # l.add_comment(
    #     doctype: "Communication",
    #     communication_type: "Comment",
    #     comment_type: comment_type || "Comment",
    #     reference_doctype: "Lead",
    #     reference_name: lead
    #     content: appointment_on,
    #     sender: "Administrator"
    # )


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
def send_whatsapp_notification(message, recipient):
    url = 'https://eu24.chat-api.com/instance18904/message?token=wada8j7hy80x6lmc'
    for number in recipient.split(','):
        payload = {'phone': number, 'body': message}
        r = requests.get(url, params=payload)
    # return r.content


@frappe.whitelist()
def update_task_ppcr():
    tasks = frappe.get_all("Task", limit=5)
    # print tasks
    for task in tasks:
        ppcr = frappe.db.count('Candidate', filters={
                               "task": task.name, "status": ("in", "Sourced", "Submitted")})
        print task.name, ppcr


# @frappe.whitelist()
# def update_emp_code():
#     checks = ["Verify Employment Check1", "Verify Employment Check2", "Verify Employment Check3", "Verify Employment Check4", "Verify Education Check1", "Verify Education Check2", "Verify Education Check3", "Verify Education Check4",
#               "Verify Address Check1", "Verify Address Check2", "Verify Address Check3", "Verify Address Check4", "Verify Family Check1", "Verify Family Check2", "Verify Family Check3", "Verify Family Check4", "Verify Reference Check1", "Verify Reference Check2",
#               "Verify Reference Check3", "Verify Reference Check4", "Verify Civil Check", "Verify Criminal Check", "Verify ID Check1", "Verify ID Check2", "Verify ID Check3", "Verify ID Check4", "Verify ID Check5",
#               "Verify ID Check6"]
#     for check in checks:
#         app = frappe.get_all(check,fields=['applicant_id'])
#         for a in app:
#             emp_id = frappe.db.get_value("Applicant", {"name": a.applicant_id},
#                                      ["client_employee_code"])
#             c = frappe.get_doc(check,{"applicant_id": a.applicant_id})
#             if c:
#                 c.update({
#                     "emp_code": emp_id
#                 })
#                 c.save(ignore_permissions=True)

# @frappe.whitelist()
# def bulk_cancel_si():
#     si_list= []
#     for i in si_list:
#         si=frappe.get_doc("Sales Invoice",i)
#         # si.cancel()
#         # frappe.delete_doc("Sales Invoice",i)
#         frappe.errprint(si)


# @frappe.whitelist()
# def mark_gst():
#     sis=frappe.get_all("Sales Invoice",fields=["customer_address","name"])
#     for si in sis:
#         # print si.customer
#         gstin=frappe.get_value("Address",si.customer_address,"gstin")
#         if gstin:
#             sii = frappe.get_doc('Sales Invoice',si.name)
#             sii.customer_gstin = gstin
#             print sii.name
#             sii.db_update()
#             frappe.db.commit()


@frappe.whitelist()
def unique_shortcode(code):
    short = frappe.get_all("Employee", fields=[
                           "short_code"], filters={"status": "Active"})
    for sc in short:
        if code == sc.short_code:
            frappe.msgprint(_("Employee Code must be unique"))


@frappe.whitelist()
def del_candidate_sc():
    # list_p = ["K1234567", "G2299501"]
    # for i in list_p:
    # # can = frappe.db.get_value("Closure","passspor_no":"K1234567")
    # can = frappe.db.get_valu("Closure",fields = ["candidate_sc"],filters={"passport_no":"K1234567"})
    # print can
        # i.candidate_sc = ""
    name_list = ["TCR01684",
                 "TCR03177",
                 "TCR09876",
                 "TCR10154",
                 "TCR03201",
                 "TCR03144",
                 "TCR03138",
                 "TCR03145",
                 "TCR03133",
                 "TCR03137",
                 "TCR03140",
                 "TCR03134",
                 "TCR03132",
                 "TCR03142",
                 "TCR03141",
                 "TCR03169",
                 "TCR03175",
                 "TCR03143",
                 "TCR03178",
                 "TCR03186",
                 "TCR03192",
                 "TCR03189",
                 "TCR03185",
                 "TCR03170",
                 "TCR03194",
                 "TCR03171",
                 "TCR03176",
                 "TCR03179",
                 "TCR03187",
                 "TCR03190",
                 "TCR03167",
                 "TCR03180",
                 "TCR03174",
                 "TCR03183",
                 "TCR03195",
                 "TCR03188",
                 "TCR03191",
                 "TCR03184",
                 "TCR03193",
                 "TCR03168",
                 "TCR03196",
                 "TCR00302",
                 "TCR00690",
                 "TCR00684",
                 "TCR00692",
                 "TCR00683",
                 "TCR00680",
                 "TCR00691",
                 "TCR00687",
                 "TCR00685",
                 "TCR00300",
                 "TCR00689",
                 "TCR00695",
                 "TCR00682",
                 "TCR00810",
                 "TCR00811",
                 "TCR00812", ]
    for i in name_list:
        can = frappe.get_doc('Closure', i)
        # frappe.db.set_value("Closure",can.name,"candidate_sc","")
        can.candidate_payment_applicable = 0
        can.candidate_sc = 0
        # can.db_update()
        can.save(ignore_permissions=True)
        # frappe.db.commit()
        print can.candidate_sc
