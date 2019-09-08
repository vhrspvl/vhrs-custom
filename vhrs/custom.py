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
from frappe.utils import cstr,formatdate, add_months, cint, fmt_money, add_days,flt
import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from frappe import throw, _, scrub
import time
from frappe.utils import today, flt, add_days, date_diff
from frappe.utils.csvutils import read_csv_content
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




def get_employees_who_are_present():
    return frappe.db.sql("""select employee
        from tabAttendance where attendance_date =%(date)s""", {"date": today()}, as_dict=True)


@frappe.whitelist()
def create_sales_order(name, customer, project, name1, passport_no, client_sc, candidate_sc, business_unit, source_executive, ca_executive, is_candidate, is_client):
    territory = frappe.db.get_value("Customer", customer, "territory")
    business_unit = frappe.get_value("Territory",territory,"business_unit")
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
                so.business_unit = business_unit
                so.department = 'Sourcing'
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
                so.business_unit = business_unit
                so.department = 'Sourcing'
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

@frappe.whitelist()
def update_task_status():
    projects = frappe.get_all('Project', {'status': (
        'in', ['Cancelled', 'Completed','DnD'])}, ['name', 'status'])
    for project in projects:
        # print project.name,project.status
        tasks = frappe.get_all('Task',{
            'project': project.name,'status': (
        'not in', ['Closed'])},['name','status'])
        for task in tasks:    
            frappe.db.set_value(
                    "Task", task.name, "status", "Closed")
            # print task.name,task.status        
        # if tasks:

def update_status():
    # projects = frappe.get_all('Project', fields={'name', 'status'})
    # for project in projects:
    #     print project.name
    #     tasks = frappe.db.get_all('Task', fields={'name', 'project', 'status'}, filters={
    #         'project': project.name})
    #     if tasks:
    #         if any(task.status == 'Open' or task.status == 'Working' or task.status == 'Pending Review' or task.status == 'Overdue' for task in tasks):
    #             frappe.db.set_value(
    #                 "Project", project.name, "status", "Open")
    #         elif all(task.status == 'Cancelled' for task in tasks):
    #             frappe.db.set_value(
    #                 "Project", project.name, "status", "Cancelled")
    #         elif all(task.status == 'DnD' for task in tasks):
    #             frappe.db.set_value(
    #                 "Project", project.name, "status", "Completed")

    customers = frappe.get_all('Customer', fields={'name', 'status'})
    for customer in customers:
        projects = frappe.db.get_all('Project', fields={'name', 'customer', 'status'}, filters={
            'customer': customer.name})
        if projects:
            if any(project.status == 'Open' or project.status == 'Overdue' or project.status == 'DnD' for project in projects):
                frappe.db.set_value(
                    "Customer", customer.name, "status", "Open")
            else:
                frappe.db.set_value(
                    "Customer", customer.name, "status", "Active")


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
                    'subash.p@voltechgroup.com',
                    ],
        subject='VHRS Active Employees - ',
        message=html
    )
    # frappe.errprint(html)


# @frappe.whitelist()
# def send_whatsapp_notification(message, recipient):
#     url = 'https://eu24.chat-api.com/instance18904/message?token=wada8j7hy80x6lmc'
#     for number in recipient.split(','):
#         payload = {'phone': number, 'body': message}
#         r = requests.get(url, params=payload)
#     return r.content

@frappe.whitelist()
def send_whatsapp_notification(message, recipient):
    url = 'https://api.wassenger.com/v1/messages'
    headers = {
    'content-type': "application/json",
    'token': "06554ceb00b8d784a61fd7f5939d1aba0b8ab2c4375774814e78428536a451e78974f816ce9ad8c7"
    }
    for number in recipient.split(','):

        payload = "{\"phone\":\"%s\",\"message\":\"%s\",\"enqueue\":\"never\"}"%(number,repr(cstr(message)))
        # payload = {'phone': number, 'message': message ,'enqueue':"never"}
        r = requests.request("POST", url, data=payload, headers=headers)
    return r.content
    # return r.content


@frappe.whitelist()
def unique_shortcode(code):
    short = frappe.get_all("Employee", fields=[
                           "short_code"], filters={"status": "Active"})
    for sc in short:
        if code == sc.short_code:
            frappe.msgprint(_("Employee Code must be unique"))


@frappe.whitelist()
def total_vacancies(project):
    query = """select sum(r1_count) as r1_total from `tabTask` where project = '%s'""" % project
    # frappe.errprint(query)
    vac = frappe.db.sql(query,as_dict=1)
    # vac = frappe.get_all("Task",fields=["r1_count"],filters={"project":project})
    for v in vac:
        tv=v.r1_total
    # frappe.errprint(tv) 
    return tv


@frappe.whitelist()
def bulk_mark_wl():
    employee = frappe.db.sql("""
    select name from `tabEmployee` where status="Active" """, as_dict=1)
    work_level = ""
    unit_head = ""
    for e in employee:
        emp = frappe.get_doc("Employee",e.name)
        if emp.designation=="Officer" or emp.designation=="Executive" or emp.designation=="Internship":
            work_level = "WL-1"
        elif emp.designation=="Sr.executive" or emp.designation=="Asst.Manager":
            work_level = "WL-2"
        elif emp.designation=="Dy.Manager" or emp.designation=="Manager" or emp.designation=="Sr.Manager":
            work_level = "WL-3"
        elif emp.designation=="Asst.General Manager" or emp.designation=="Dy.General Manager" or emp.designation=="Sr.General Manager":
            work_level = "WL-4"
        elif emp.designation=="Asst.Vice President" or emp.designation=="Dy.Vice President" or emp.designation=="Sr.Vice President":
            work_level = "WL-5"
        elif emp.designation=="President" or emp.designation=="Executive Director" or emp.designation=="Advisors":
            work_level = "WL-6"
        elif emp.designation=="Director" or emp.designation=="Managing Director":
            work_level = "WL-7"
        elif emp.designation=="Chairman":
            work_level = "WL-8"
        if not emp.work_level:
            emp.update({
                "work_level": work_level
            })
            emp.save(ignore_permissions=True)
            frappe.db.commit()
        if emp.business_unit == "BUHR-1":
            unit_head = "sangeetha.s@voltechgroup.com"
        elif emp.business_unit == "BUHR-2":
            unit_head = "jagan.k@voltechgroup.com"
        elif emp.business_unit == "BUHR-3":
            unit_head = "selvaraj.g@voltechgroup.com"
        elif emp.business_unit == "Common":
            unit_head = "dineshbabu.k@voltechgroup.com"
        elif emp.business_unit == "BUHR-4":
            unit_head = "kalyanasundaram.p@voltechgroup.com"
        emp.update({
            "unit_head": unit_head
        })
        emp.save(ignore_permissions=True)
        frappe.db.commit()



@frappe.whitelist()
def removeduplicateatt():
    get_att = frappe.db.sql("""SELECT name FROM `tabAttendance` WHERE attendance_date = %s GROUP BY employee
                    HAVING COUNT(employee) >1""",(today()),as_dict=1)
    if get_att:                 
        for att in get_att:                 
            obj = frappe.get_doc("Attendance",att["name"])
            obj.db_set("docstatus", 2)
            frappe.delete_doc("Attendance", obj.name)
            frappe.db.commit()

# @frappe.whitelist()
# def update_pm_manager(doc, method):
#     if doc.employee_code:
#         pmm = frappe.db.get_value("Performance Management Manager", {
#                                       "employee_code": doc.employee_code})
#         if pmm:
#             epmm = frappe.get_doc("Performance Management Manager", pmm)
#         else:
#             epmm = frappe.new_doc("Performance Management Manager")
#         month = ""
#         if doc.date_of_rating:
#             objDate = datetime.strptime(doc.date_of_rating, '%Y-%m-%d')
#             month = datetime.strftime(objDate,'%b%Y')
#         epmm.update({
#             "employee_code": doc.employee_code,
#             "employee_name": doc.employee_name,
#             "short_code": doc.short_code,
#             "department": doc.department,
#             "designation": doc.designation,
#             "business_unit": doc.business_unit,
#             "branch": doc.branch,
#             "work_level": doc.work_level,
#             "date_of_joining": doc.date_of_joining,
#             "date_of_rating": today(),
#             "operations_manager": doc.operations_manager,
#             "unit_head": doc.unit_head,
#             "month": month
#         })
#         epmm.set('kra_rating_manager', [])
#         child = doc.kra_rating_self
#         for c in child:
#             epmm.append("kra_rating_manager",{
#                 "description": c.description,
#                 "weightage": c.weightage,
#                 "self_rating": c.self_rating
#             })
#         epmm.save(ignore_permissions=True)



# @frappe.whitelist()
# def update_pm_reviewer(doc, method):
#     if doc.employee_code:
#         month = ""
#         pmm = frappe.db.get_value("Performance Management Reviewer", {
#                                       "employee_code": doc.employee_code})
#         if pmm:
#             epmm = frappe.get_doc("Performance Management Reviewer", pmm)
#         else:
#             epmm = frappe.new_doc("Performance Management Reviewer")
#         if doc.date_of_rating:
#             objDate = datetime.strptime(doc.date_of_rating, '%Y-%m-%d')
#             month = datetime.strftime(objDate,'%b%Y')
#         epmm.update({
#             "employee_code": doc.employee_code,
#             "employee_name": doc.employee_name,
#             "short_code": doc.short_code,
#             "department": doc.department,
#             "designation": doc.designation,
#             "business_unit": doc.business_unit,
#             "branch": doc.branch,
#             "work_level": doc.work_level,
#             "date_of_joining": doc.date_of_joining,
#             "date_of_rating": today(),
#             "operations_manager": doc.operations_manager,
#             "unit_head": doc.unit_head,
#             "month": month
#         })
#         epmm.set('kra_rating_reviewer', [])
#         child = doc.kra_rating_self
#         for c in child:
#             epmm.append("sales_target",{
#                 "description": c.description,
#                 "weightage": c.weightage,
#                 "self_rating": c.self_rating,
#                 "manager": c.manager
#             })
#         epmm.save(ignore_permissions=True)
        

@frappe.whitelist()
def update_pm_basic():
    employee = frappe.db.sql("""
    select name from `tabEmployee` where employment_type!="Contract" and status="Active" and branch!= "Nepal" and branch!="vsdc" """, as_dict=1)
    for e in employee:
        if e.name:
            doc = frappe.get_doc("Employee",e.name)
            if doc.operations_manager:
                op = doc.operations_manager
            else:
                op = "-"
            objDate = datetime.strptime('2019-08-01', '%Y-%m-%d')
            month = datetime.strftime(objDate,'%b%Y')
            emp_pm_id = frappe.db.get_value("Performance Management", {
                                      "employee_code": e.name,"month":month})
            if emp_pm_id:
                emp_pm = frappe.get_doc("Performance Management", emp_pm_id)
            else:
                emp_pm = frappe.new_doc("Performance Management")
            emp_pm.update({
                "employee_code": e.name,
                "user_id": doc.user_id,
                "employee_name": doc.employee_name,
                "short_code": doc.short_code,
                "department": doc.department,
                "designation": doc.designation,
                "business_unit": doc.business_unit,
                "branch": doc.branch,
                "role": doc.role,
                "work_level": doc.work_level,
                "date_of_joining": doc.date_of_joining,
                "date_of_rating": today(),
                "operations_manager": op,
                "unit_head": doc.second_reviewer,
                "month":month,
                "pending": "Self",
                "kra_rating_reviewer": []
            })
            emp_pm.append("kra_rating_reviewer", {
                })
            emp_pm.save(ignore_permissions=True)
            frappe.db.commit()


@frappe.whitelist()
def generate_qr(closure):
    closure = frappe.get_doc("Closure",closure)
    import qrcode
    # Create qr code instance
    qr = qrcode.QRCode(
        version = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_H,
        box_size = 4,
        border = 4,
    )
    # The data that you want to store
    data = """Closure ID:%s \n
    Candidate Name:%s \n
    PP No:%s \n    
        """%(closure.name,closure.name1,closure.passport_no)
    # Add data
    qr.add_data(data)
    qr.make(fit=True)
    # Create an image from the QR Code instance
    img = qr.make_image()
    path = os.path.join('/media/vhrs/ERP/',
                                'public', 'files')
    print path
    qr_name = closure.name + '_qr.png'
    img.save(path +"/%s"% qr_name)
    frappe.db.set_value("Closure",closure.name,"qr_code","/files/%s"%qr_name)
    return qr_name


@frappe.whitelist()
def update_holiday_attendance():
    y_date = datetime.strptime(add_days(today(),-1), "%Y-%m-%d").date()
    employee = frappe.db.sql("""
    select name from `tabEmployee` where employment_type!="Contract" and status="Active" """, as_dict=1)
    for e in employee:
        holiday_list = frappe.db.get_value(
        "Employee", {'employee': e.name}, ['holiday_list'])
        if holiday_list:
            holiday_dates = frappe.db.get_all(
                "Holiday", filters={'holiday_date': y_date, 'parent': holiday_list},fields=["holiday_date"])
            if holiday_dates:
                attendance = frappe.db.exists("Attendance",{"attendance_date":y_date,"employee":e.name})
                att = "Not Ok"
                if attendance:
                    attendance = frappe.get_doc("Attendance",attendance)
                    ha = frappe.new_doc("Holiday Attendance")
                    ha.update({
                        "employee": attendance.employee,
                        "employee_name": attendance.employee_name,
                        "attendance_date": attendance.attendance_date,
                        "company": attendance.company,	
                        "status": attendance.status,		
                    })
                    ha.save(ignore_permissions=True)
                    ha.submit()
                    frappe.db.commit()
                    att = "ok"
                if att == "ok":
                    attendance.cancel()

def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n)


@frappe.whitelist()
def mark_od():
    attendance_date = date.today()
    # attendance_date = datetime.strptime(add_days(today(),-1), "%Y-%m-%d").date()
    start_date = get_first_day(attendance_date)
    end_date = get_last_day(attendance_date)
    od_record = frappe.db.sql("""select employee, half_day,name, from_date,to_date from `tabOn Duty Application`
                where from_date and to_date between %s and %s and status = 'Approved'
                  and docstatus = 1""", (start_date,end_date), as_dict=True)
    
    for od in od_record:
        att = frappe.db.sql("""select employee, attendance_date,name as name from tabAttendance where employee = %s and attendance_date between %s and %s and docstatus = 1""",(od.employee,od.from_date,od.to_date),as_dict=True)
        # print od.name
        if att:
            for at in att:
                # print at.name
                attendance= frappe.get_doc("Attendance",at.name)
                attendance.update({
                                "status":"Present",
                                "onduty_link":od.name
                                })
                attendance.db_update()
                frappe.db.commit()
                            

def get_first_day(dt, d_years=0, d_months=0):
    # d_years, d_months are "deltas" to apply to dt
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m - 1, 12)
    return date(y + a, m + 1, 1)


def get_last_day(dt):
    return get_first_day(dt, 0, 1) + timedelta(-1)

# @frappe.whitelist()
# def update_tn():
#     # attendance_date = date.today()
#     attendance_date = datetime.strptime(add_days(today(),-6), "%Y-%m-%d").date()
#     start_date = get_first_day(attendance_date)
#     end_date = get_last_day(attendance_date)
#     # day = today()
#     tn_record = frappe.db.sql("""select name, in_time ,out_time from `tabAttendance`
#                 where attendance_date between %s and %s and branch = "T.Nagar"
#                   """, (start_date,end_date), as_dict=True)
    
    
#     # att_ids = frappe.get_list('Attendance', filters={"shift": "A",
#                                                     #  "docstatus": 0, "attendance_date": day})
#     for tn in tn_record:
#         if tn:
            
#             if tn.in_time >= '08:45:00' and tn.out_time <= '18:15:00':
#                 att= frappe.get_doc("Attendance",tn.name) 
#                 print att.out_time
#                 # att.update({
#                 #             "status": "Half Day"
#                 #         })
#                 # att.db_update()
#                 # frappe.db.commit()

@frappe.whitelist()
def load_candidates(task):
    candidates = []
    for candidate in get_candidates(task):
        candidates.append(frappe._dict({
            "passport_no": candidate.passport_no,
            "pending_for": candidate.pending_for,
            "given_name": candidate.given_name,
            "india_experience": candidate.india_experience,
            "gulf_experience": candidate.gulf_experience,
            "current_ctc": candidate.current_ctc,
            "currency_type": candidate.currency_type,
            "expected_ctc": candidate.expected_ctc,
            "currency_type1": candidate.currency_type1,
            "expiry_date": candidate.expiry_date,
            "ecr_status": candidate.ecr_status,
            "current_location": candidate.current_location,
            "mobile": candidate.mobile,
            "landline": candidate.landline,
            "skype_id": candidate.skype_id,
            "associate_name": candidate.associate_name,
            "contact_email": candidate.contact_no,
            "email": candidate.email,
            "candidate_id": candidate.name
            }))
    return candidates        
            

def get_candidates(task):
    candidates = frappe.get_all("Candidate", "*", {"task": task}, order_by="given_name asc")
    return candidates 

def update_tasks():
    tasks = frappe.get_all("Task")
    # print len(tasks)
    for task in tasks:
        t = frappe.get_doc("Task",task)
        candidates = t.candidates
        sourced = 0
        shortlisted = 0
        interviewed = 0
        proposed_psl = 0
        sourced = frappe.db.count('Candidate', {'task':t.name,'pending_for': ('in',['Sourced','Submitted'])})
        shortlisted = frappe.db.count('Candidate', {'task':t.name,'pending_for': 'Shortlisted'})
        interviewed = frappe.db.count('Candidate', {'task':t.name,'pending_for': 'Interviewed'})
        proposed_psl = frappe.db.count('Candidate', {'task':t.name,'pending_for': 'Proposed PSL'})
        print t.r7_count
        t.r7_count = sourced
        t.r4_count = shortlisted
        t.r6_count = interviewed
        t.r3_count = proposed_psl
        # print t.name, sourced
        if t.r1_count:
            ppcr = t.r1_count * t.proposition
            t.pending_profiles_to_send = ppcr - (t.r7_count + t.r4_count + t.r3_count)
        # t.save()
        t.db_update()
        frappe.db.commit()

@frappe.whitelist()
def create_user_permission(e_code,op_manager):
    frappe.errprint(e_code)
    frappe.errprint(op_manager)
    # if not frappe.db.exists('User Permission',{'for_value':e_code})
    #     frappe.errprint(e_code)
        # up=frappe.new_doc(User Permission)
        # up.user = op_manager
        # up.allow ="Employee"
        # up.for_value = e_code

@frappe.whitelist()
def mark_dnd_incharge(dnd,project):
    frappe.errprint(dnd)
    closures = frappe.get_all('Closure',{'project':project})
    for closure in closures:
        frappe.errprint(closure)
        closure = frappe.get_doc("Closure",closure)
        closure.dnd_incharge = dnd
        closure.db_update()


@frappe.whitelist()
def get_pp_no():
    per = frappe.get_all("Payment Entry Reference",['name','reference_doctype','reference_name'],{'reference_doctype':'Sales Invoice','docstatus':('!=',"2")})
    for p in per:
        ppno = frappe.get_value(p.reference_doctype,p.reference_name,"passport_no")
        if ppno:
            frappe.set_value("Payment Entry Reference",p.name,"passport_number",ppno)


@frappe.whitelist()
def get_visitor_history(mobile):
    visitor = []
    for v in get_visitor(mobile):
        visitor.append(frappe._dict({
            "date": visitor.date,
            "in_time": visitor.in_time,
            "out_time": visitor.out_time,
            "to_meet": visitor.to_meet,
            "purpose": visitor.purpose,
            }))
    return visitor       
            

def get_visitor(mobile):
    visitor = frappe.get_all("Visitor Register", "*", {"mobile": mobile}, order_by="date desc")
    return visitor

@frappe.whitelist()
def on_duty_bulk_mark():
    from_date = '2019-08-01'
    to_date = '2019-08-31'
    ods = frappe.db.sql("""select name,employee,status from `tabOn Duty Application` where from_date between %s and %s """,(from_date,to_date),as_dict=1)
    for od in ods:
        print od.status
        if od.status == "Approved":
            doc= frappe.get_doc("On Duty Application",od.name)
            print doc.name
            request_days = date_diff(doc.to_date, doc.from_date) + 1
            for number in range(request_days):
                attendance_date = add_days(doc.from_date, number)
                skip_attendance = validate_if_attendance_not_applicable(
                    doc.employee, attendance_date)
                if not skip_attendance:
                    att = frappe.db.exists(
                        "Attendance", {"employee": doc.employee, "attendance_date": attendance_date})
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
                        if attendance_date <= date.today():
                            attendance = frappe.new_doc("Attendance")
                            attendance.employee = doc.employee
                            attendance.employee_name = doc.employee_name
                            attendance.status = "Present"
                            attendance.attendance_date = attendance_date
                            attendance.in_time = ""
                            attendance.out_time = ""
                            attendance.onduty_status = "On Duty"
                            attendance.company = doc.company
                            attendance.save(ignore_permissions=True)
                            attendance.submit()


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

def salesin_div():

    div = frappe.db.sql(""" select name from `tabPurchase Invoice` where business_unit in ('BUHR-2')""", as_dict = 1)
    div1 = frappe.db.sql(""" select name from `tabPurchase Invoice` where business_unit in ('BUHR-1','BUHR-3')""", as_dict = 1)
    # print len(div1)
    # for d in div:
    #     d1 = frappe.get_doc("Purchase Invoice",d)
    #     print d1.name
    #     d1.division = "S1"
    #     d1.db_update()
    #     frappe.db.commit()
    for s in div1:
        s2 = frappe.get_doc("Purchase Invoice",s)
        print s2.name
        s2.division = "S2"
        s2.db_update()
        frappe.db.commit()
def bulk_update():
    # employee = frappe.get_all("Employee",fields = ['user_id'])
    # employee = frappe.db.sql(""" select name from `tabEmployee` where user_id = lead_owner""", as_dict = 1)
    lead = frappe.get_all("Lead",limit = 5)
    employee = frappe.get_all("Employee",filters = {"status":"Active"})
    print employee
    # print len(tasks)
    # for e in employee:
    #     emp = frappe.get_doc("Employee",e)
    #     # print emp.user_id
    #     if emp.user_id:
    #         for l in lead:
    #             l1 = frappe.get_doc("Lead",l)
    #             if l1.lead_owner == emp.user_id:
    #                 l1.division = emp.division
    #                 l1.db_update()
    #                 frappe.db.commit()

                    # print emp.division

# def customer_group():
#     cg = frappe.db.sql(""" select name from `tabCustomer` where customer_class in ('Dormant')""", as_dict = 1)
#     print len(cg)
    # for c in cg:
    #     c1 = frappe.get_doc("Customer",c)
    #     # print c1.customer_class
    #     c1.customer_group = "Dormant"
    #     c1.db_update()
    #     frappe.db.commit()
def created_on():
    customer = frappe.get_all("Customer")
    # print customer
    
    for c in customer:
        cust = frappe.get_doc("Customer",c)
        # print cust.customer_class
        day = '31-12-2018'
        date = datetime.strptime("2018-12-31","%Y-%m-%d")
        # print type(cust.creation)
        # print cust.creation
        if cust.creation <date:
            print cust.name,cust.creation
            # print c1.customer_class
            cust.customer_group = "Existing Account"


        

        

    

    
# @frappe.whitelist()
# def saturday():
#     # day = date.today()
#     day = '2019-08-24'
#     total_working_hours = 0
#     worked_hrs = 0
#     att_ids = frappe.get_all('Attendance', filters={"attendance_date": day, "company": "Voltech HR Services Private Limited", "business_unit": ('!=', 'BUHR-4')})
#     for att_id in att_ids:
#         # print att_id
#         if att_id:
#             att = frappe.get_doc("Attendance", att_id)
#             if att.in_time and not att.out_time:
#                 att.update({
#                     "total_working_hour": "",
#                     "status": "Absent"
#                 })
#                 att.db_update()
#                 frappe.db.commit()
#             elif att.in_time and att.out_time:
#                 in_time_f = datetime.strptime(
#                     att.in_time, '%H:%M:%S')
#                 out_time_f = datetime.strptime(
#                     att.out_time, '%H:%M:%S')
#                 worked_hrs = out_time_f - in_time_f
#                 working_hrs = str(worked_hrs)
#                 total_working_hour = datetime.strptime(
#                     working_hrs, '%H:%M:%S')
#                 total_working_hours = total_working_hour.strftime('%H:%M:%S')
#                 # print att.employee_name, total_working_hours
#                 # print total_working_hours
#                 hours=timedelta(hours=total_working_hour.hour, minutes=total_working_hour.minute, seconds=total_working_hour.second)
#                 f_max = timedelta(hours = 9.5)
#                 h_max = timedelta(hours =5)
#                 if att.shift == "C":
#                     c_max = timedelta(hours = 9)
#                     if hours >= c_max:
#                         status = "Present"
#                     elif hours >= h_max:
#                         status = "Half Day"
#                     else:
#                         status = "Absent"
#                     # print hours,status
#                 elif att.status == "On Duty":
#                     pass
#                 # elif hours >= f_max:
#                 #     status = "Present"
#                 elif hours >= h_max:
#                     status = "Present"
#                 else:
#                     status = "Absent"
#                 print att.employee_name, att.in_time,att.out_time,hours,status
#                 att.update({
#                     "total_working_hour": total_working_hours,
#                     "status": status
#                 })
#                 att.db_update()
#                 frappe.db.commit()
            