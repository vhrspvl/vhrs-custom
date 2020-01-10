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
import itertools
from frappe.utils import today, flt, add_days, date_diff
from frappe.utils.csvutils import read_csv_content
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee, is_holiday
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
def generate_qr(candidate):
    can = frappe.get_doc("Candidate",candidate)
    import qrcode
    import qrcode.image.pil
    from PIL import Image



    # Create qr code instance
    qr = qrcode.QRCode(
        version = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_H,
        box_size = 4,
        border = 4,
    )
   
    # The data that you want to store
    data = """Candidate Name:%s\nPP No:%s\nCustomer:%s\nProject:%s\nTask:%s\nTCR No.:%s"""%(can.given_name,can.passport_no,can.customer,can.project,can.task,can.name)
    # Add data
    qr.add_data(data)
    qr.make(fit=True)
    # Create an image from the QR Code instance
    img = qr.make_image()
    path = os.path.join('/media/vhrs/ERP/','public', 'files')
    qr_name = can.passport_no + '_qr.png'
    # basewidth = 64
    # wpercent = (basewidth / float(img.size[0]))
    # hsize = int((float(img.size[1]) * float(wpercent)))
    # img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    img.save(path +"/%s"% qr_name)
    frappe.errprint(img.size)
    frappe.db.set_value("Candidate",can.name,"qr_code","/files/%s"%qr_name)
    frappe.db.set_value("Closure",{"candidate":can.name},"qr_code","/files/%s"%qr_name)
    return qr_name

@frappe.whitelist()
def load_candidates(task):
    candidates = frappe.get_all("Candidate", "*", {"task": task}, order_by="given_name asc")
    return candidates

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
    select name,project from tabClosure""", as_dict=1)
    for closure in closures:
        dnd_incharge = frappe.db.get_value(
            "Project", closure["project"], "dnd_incharge")
        if dnd_incharge:
            closure = frappe.get_doc("Closure", closure["name"])
            closure.dnd_incharge = dnd_incharge
            closure.db_update()

@frappe.whitelist()
def dnd_onboarding_date(date,project):
    closures = frappe.get_list('Closure',{'project':project},['name'])
    for closure in closures:
        clo = frappe.get_doc('Closure',closure.name)
        clo.dnd_onboarding_date = date
        clo.db_update()
    return closures

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
def create_sales_order(name, customer, project, name1, passport_no,designation, client_sc, candidate_sc, business_unit, source_executive, ca_executive, is_candidate, is_client):
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
            item.qty = "1"
            # item.append("item_defaults", {
            #         "company":  frappe.defaults.get_user_default("Company"),
            #     })
            item.is_stock_item = "0"
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
                so.department = 'Sourcing - VHRS'
                # so.source_executive = source_executive
                # so.ca_executive = ca_executive
                so.append("items", {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "payment_type": "Candidate",
                    "description": item.description,
                    "uom": item.stock_uom,
                    "is_stock_item" : "0",
                    "passport_no" : passport_no,
                    "designation" : designation,
                    "qty":"1",
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
                so.department = 'Sourcing - VHRS'
                # so.source_executive = source_executive
                # so.ca_executive = ca_executive
                so.append("items", {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "payment_type": "Client",
                    "description": item.description,
                    "uom": item.stock_uom,
                    "passport_no" : passport_no,
                    "designation" : designation,
                    "qty":"1",
                    "is_stock_item" :"0",
                    "rate": client_sc,
                    "delivery_date": today()
                })
                so.insert()
                so.submit()
                so.save(ignore_permissions=True)
            total = cint(candidate_sc) + cint(client_sc)

            return "Sales Order Created for Total value {0}".format(frappe.bold(fmt_money(total, currency='INR')))


@frappe.whitelist()
def recreate_sales_order(name, customer, project, name1, passport_no,designation, redeputation_cost):
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
            item.qty = "1"
            item.is_stock_item = "0"
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
                    "is_stock_item" : "0",
                    "passport_no" : passport_no,
                    "designation" : designation,
                    "qty":"1",
                    "rate": redeputation_cost,
                    "delivery_date": today()
                })
                so.insert()
                so.submit()
                so.save(ignore_permissions=True)

            return "Sales Order Created for Total value {0}".format(frappe.bold(fmt_money(redeputation_cost, currency='INR')))

@frappe.whitelist()
def update_task_status():
    tasks = frappe.get_all('Project',{'territory':'India'},['name'])
    # print tasks
    for t in tasks:
        frappe.db.set_value(
                    "Project", t.name, "project_type",'CVS - Shared')

    # projects = frappe.get_all('Project', {'status':'Completed','operation_status':'Completed'}, ['name', 'status','operation_status'])
    # for project in projects:
    #     print project.name,project.status,project.operation_status
    #     tasks = frappe.get_all('Task',{
    #         'project': project.name,'status': (
    #     'not in', ['Completed'])},['name','status'])
    #     for task in tasks:    
    #         frappe.db.set_value(
    #                 "Task", task.name, "status", "Completed")

    # projects = frappe.get_all('Project', {'status':'Cancelled','operation_status':'Completed'}, ['name', 'status','operation_status'])
    # for project in projects:
    #     print project.name,project.status,project.operation_status
    #     tasks = frappe.get_all('Task',{
    #         'project': project.name,'status': (
    #     'not in', ['Completed'])},['name','status'])
    #     for task in tasks:    
    #         frappe.db.set_value(
    #                 "Task", task.name, "status", "Completed")                
            # print task.name,task.status        
        # if tasks:
@frappe.whitelist()
def update_task_status1():
    projects = frappe.get_all('Project', {'project_type':'External','department':'Sourcing - VHRS','operation_status':'Completed'}, ['name', 'status','operation_status','project_type','department'])
    for p in projects:
        # print p.name,p.project_type,p.department
        tasks = frappe.get_all('Task',{
            'project': p.name,'status': (
        'not in', ['Completed'])},['name','status'])
        for task in tasks:    
            frappe.db.set_value(
                    "Task", task.name, "status", "Completed")
        frappe.db.set_value(
                    "Project", p.name, "status", "Completed")  
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


@frappe.whitelist()
def send_whatsapp_notification(message, recipient,lat=None,lng=None,address=None,filename=None):
    url = 'https://eu2.chat-api.com/instance86401/message?token=bfhq1v1qnuww5pla'
    for number in recipient.split(','):
        payload = {'phone': number, 'body': message}
        r = requests.get(url, params=payload)  
    if filename:
        url = 'https://eu2.chat-api.com/instance86401/sendFile?token=bfhq1v1qnuww5pla'
        for number in recipient.split(','):
            payload = {'phone': number, 'body': 'http://erp.voltechgroup.com'+filename, 'filename':'erp-profile',"caption": "ERP Profile"}
            r = requests.get(url, params=payload) 
            frappe.errprint(payload)  
            frappe.errprint(r.content)    
    if lat and lng and address:
        url = 'https://eu2.chat-api.com/instance86401/sendLocation?token=bfhq1v1qnuww5pla'
        for number in recipient.split(','):
            payload = {'phone': number, 'lat': lat, 'lng':lng,"address": address}
            r = requests.get(url, params=payload) 
            frappe.errprint(payload)  
            frappe.errprint(r.content)  
    return r.content

# @frappe.whitelist()
# def send_whatsapp_notification(message, recipient):
#     url = 'https://api.wassenger.com/v1/messages'
#     headers = {
#     'content-type': "application/json",
#     'token': "06554ceb00b8d784a61fd7f5939d1aba0b8ab2c4375774814e78428536a451e78974f816ce9ad8c7"
#     }
#     for number in recipient.split(','):

#         payload = "{\"phone\":\"%s\",\"message\":\"%s\",\"enqueue\":\"never\"}"%(number,repr(cstr(message)))
#         # payload = {'phone': number, 'message': message ,'enqueue':"never"}
#         r = requests.request("POST", url, data=payload, headers=headers)
#     return r.content
#     # return r.content


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
    frappe.errprint(query)
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
            


def update_tasks():
    tasks = frappe.get_all("Task")
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
        # print t.r7_count
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



def salesin_div():

    div = frappe.db.sql(""" select name from `tabSales Invoice` where business_unit in ('BUHR-2')""", as_dict = 1)
    div1 = frappe.db.sql(""" select name from `tabSales Invoice` where business_unit in ('BUHR-1','BUHR-3')""", as_dict = 1)
    print len(div)
    for d in div:
        d1 = frappe.get_doc("Sales Invoice",d)
        print d1.name
        d1.division = "S1"
        d1.db_update()
        frappe.db.commit()
    # for s in div1:
    #     s2 = frappe.get_doc("Sales Invoice",s)
    #     print s2.name
    #     s2.division = "S2"
    #     s2.db_update()
    #     frappe.db.commit()
def salesorder_div():
    
    div = frappe.db.sql(""" select name from `tabSales Order` where business_unit in ('BUHR-2')""", as_dict = 1)
    div1 = frappe.db.sql(""" select name from `tabSales Order` where business_unit in ('BUHR-1','BUHR-3')""", as_dict = 1)
    print len(div)
    for d in div:
        d1 = frappe.get_doc("Sales Order",d)
        print d1.name
        d1.division = "S1"
        d1.db_update()
        frappe.db.commit()
    # for s in div1:

    #     s2 = frappe.get_doc("Sales Order",s)'''  '''
    #     print s2.name
    #     s2.division = "S2"
    #     s2.db_update()'''  '''
    #     frappe.db.commit()
def purchase_in():
    div = frappe.db.sql(""" select name from `tabPurchase Invoice` where business_unit in ('BUHR-2')""", as_dict = 1)
    div1 = frappe.db.sql(""" select name from `tabPurchase Invoice` where business_unit in ('BUHR-1','BUHR-3') and division not in ('S2')""", as_dict = 1)
    div2 =  frappe.db.sql(""" select name from `tabPurchase Invoice` where business_unit ="Common" and division is null  """,  as_dict = 1)
    print len(div)
    for p in div:
        p1 = frappe.get_doc("Purchase Invoice",p)
        print p1.division
        p1.division = "S1"
        p1.db_update()
        frappe.db.commit()
    print len(div2)
    for p in div2:
        p1 = frappe.get_doc("Purchase Invoice",p)
        print p1.division
        p1.division = "CMN"
        p1.db_update()
        frappe.db.commit()
def expense_claim():
    div = frappe.db.sql(""" select name from `tabExpense Claim` where division is null  """,  as_dict = 1)
    print len(div)
    for d in div:
        d1 = frappe.get_doc("Expense Claim",d)
        print d1.division
        d1.division = "CMN"
        d1.db_update()
        frappe.db.commit()

def supplier_group():
    purchase_in = frappe.get_all("Purchase Invoice",['name','supplier'])
    for p in purchase_in:
        supplier_group = frappe.get_value('Supplier',{'name':p.supplier},['supplier_group'])
        pi = frappe.get_doc('Purchase Invoice',p.name)
        pi.supplier_group = supplier_group
        pi.db_update()
        frappe.db.commit()     
       



def payment_div():
    
    div = frappe.db.sql(""" select name from `tabPayment Entry` where business_unit in ('BUHR-2')""", as_dict = 1)
    div1 = frappe.db.sql(""" select name from `tabPayment Entry` where business_unit in ('BUHR-1','BUHR-3')""", as_dict = 1)
    # print len(div1)
    # for d in div:
    #     d1 = frappe.get_doc("Payment Entry",d)
    #     print d1.name
    #     d1.division = "S1"
    #     d1.db_update()
    #     frappe.db.commit()
    for s in div1:

        s2 = frappe.get_doc("Payment Entry",s)
        print s2.name
        s2.division = "S2"
        s2.db_update()
        frappe.db.commit()
def expense_div():
    expense = frappe.get_all("Expense Claim",{'division':"S2"},['name','employee'])
    print expense
    # for e in expense:
    #     pm = frappe.get_value("Employee",{'name':e.employee},['division'])
        # print pm
        # if pm == "CMN":
            # print pm
            # e1 = frappe.get_doc("Expense Claim",e)
            # print e1
            # e1.division = pm
            # e1.db_update()
            # frappe.db.commit()
            # print e1.division


            # t1 = frappe.get_doc("Expense Claim",e)
        #     t1.division = pm
    #         t1.db_update()
    #         frappe.db.commit()

    #     if not t1.project_manager:
    #         t1.project_manager = pro.project_manager
    #         t1.db_u
    # div = frappe.db.sql(""" select name from `tabExpense Claim` where business_unit in ('BUHR-2')""", as_dict = 1)
    # div1 = frappe.db.sql(""" select name from `tabExpense Claim` where business_unit in ('BUHR-1','BUHR-3')""",as_dict = 1)
    

    # print len(div)
    # for d in div:
    #     d1 = frappe.get_doc("Expense Claim",d)
    #     print d1.name
    #     d1.division = "S1"
    #     d1.db_update()
    #     frappe.db.commit()
    # for s in div1:
    
    #     s2 = frappe.get_doc("Expense Claim",s)
    #     print s2.name
    #     s2.division = "S2"
    #     s2.cancel()
    #     frappe.db.commit()


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
def task():
    task = frappe.get_all("Task")
    project = frappe.get_all("Project")
    # print task
    for p in project:
        proj = frappe.get_doc("Project",p)
        # print proj.project_manager
        if proj.project_manager:
            for t in task:
                t1 = frappe.get_doc("Task",t)
                if t1.project_manager == proj.project_manager:
                    print proj.project_manager
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
            cust.db_update()
            frappe.db.commit()
        


@frappe.whitelist()
def saturday():
    # day = date.today()
    day = '2020-01-01'
    att_ids = frappe.get_all('Attendance', filters={"attendance_date": day, "company": "Voltech HR Services Private Limited"})
    for att_id in att_ids:
        if att_id:
            att = frappe.get_doc("Attendance", att_id)
            if att.status == 'Half Day':
                print att.status
                att.update({
                    "status": "Present"
                })
                att.db_update()
                frappe.db.commit()
           
            
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
def create_compact_item_print_custom_field():
    	create_custom_field('Sales Invoice', {
		'label': _('Vehicle No'),
		'fieldname': 'vehicle_no',
		'fieldtype': 'Data',
		'print_hide': 1,
		'insert_after': 'lr_no',
        'translatable': 0
	})

@frappe.whitelist()
def get_approvers(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("employee"):
		frappe.throw(_("Please select Employee Record first."))

	approvers = []
	department_details = {}
	department_list = []
	employee_department = filters.get("department") or frappe.get_value("Employee", filters.get("employee"), "department")
	if employee_department:
		department_details = frappe.db.get_value("Department", {"name": employee_department}, ["lft", "rgt"], as_dict=True)
	if department_details:
		department_list = frappe.db.sql("""select name from `tabDepartment` where lft <= %s
			and rgt >= %s
			and disabled=0
			order by lft desc""", (department_details.lft, department_details.rgt), as_list = True)

	if filters.get("doctype") == "On Duty Application":
		parentfield = "leave_approvers"
	else:
		parentfield = "expense_approvers"
	if department_list:
		for d in department_list:
			approvers += frappe.db.sql("""select user.name, user.first_name, user.last_name from
				tabUser user, `tabDepartment Approver` approver where
				approver.parent = %s
				and user.name like %s
				and approver.parentfield = %s
				and approver.approver=user.name""",(d, "%" + txt + "%", parentfield), as_list=True)

	return approvers

@frappe.whitelist()
def update_task_operation_Status(doc,method):
    tasks = frappe.get_all('Task',{
        'project': doc.name,'status': (
        'not in', ['Completed'])},['name','operation_status','project_manager'])
    for task in tasks:
        frappe.db.set_value("Task", task.name, "operation_status",doc.operation_status)
        frappe.db.set_value("Task", task.name, "project_manager",doc.project_manager)
        frappe.db.set_value("Task", task.name, "territory",doc.territory)

@frappe.whitelist()
def update_last_sync():
    shift = frappe.get_list("Shift Type")
    for s in shift:
        # doc = frappe.get_doc("Shift Type",s)
        print datetime.now()
        frappe.db.set_value("Shift Type",s, "last_sync_of_checkin",datetime.now())


@frappe.whitelist()
def update_candidates(candidate):
    frappe.errprint(candidate)
    can = json.loads(candidate)
    for c in can:
        cand = frappe.get_doc("Candidate",(c["candidate_id"]))
        cand.update({
            "pending_for": c["pending_for"],
            "degree" : c.get("degree"),
            "specialization" : c.get("specialization"),
            "current_ctc" :c.get("current_ctc"),
            "current_ctc" :c.get("current_ctc"),
            "indian_experience" : c.get("indian_experience"),
            "gulf_experience" : c.get("gulf_experience"),
            "currency_type" : c.get("currency_type"),
            "expected_ctc" : c.get("expected_ctc"),
            "passport_no" : c.get("passport_no"),
            "expiry_date" : c.get("expiry_date"),
            "ecr_status" : c.get("ecr_status"),
            "current_location" : c.get("current_location"),
            "mobile" : c.get("mobile"),
            "associate_name" : c.get("associate"),
            "user" : c.get("user"),
        })
        cand.db_update()
        frappe.db.commit()



# def update_pp():
#     candidates = frappe.db.sql("""select name from `tabCandidate` where `passport_no` is null and `pending_for`='Proposed PSL' and `territory` != 'India' and date(`creation`) between '2019-04-01' and '2019-11-11' """,as_dict=1)
#     print candidates
#     for can in candidates:
#         if frappe.db.exists("Closure",{'candidate':can.name}):
#             closure = frappe.get_doc("Closure",{'candidate':can.name})
#             if closure.passport_no:
#                 # print closure.name, closure.passport_no, can.name
#                 cand = frappe.get_doc("Candidate",can.name)
#                 cand.update({
#                     "passport_no" : closure.passport_no,
#                 })
#                 cand.flags.ignore_mandatory=True
#                 cand.db_update()
#                 frappe.db.commit()
def update_pp():
    candidates = frappe.db.sql("""select name from `tabCandidate` where `passport_no` is null and `pending_for`='Proposed PSL' and `territory` != 'India' and date(`creation`) between '2019-04-01' and '2019-11-11' """,as_dict=1)
    print candidates
    for can in candidates:
        if frappe.db.exists("Closure",{'candidate':can.name}):
            closure = frappe.get_doc("Closure",{'candidate':can.name})
            if closure.passport_no:
                # print closure.name, closure.passport_no, can.name
                cand = frappe.get_doc("Candidate",can.name)
                cand.update({
                    "passport_no" : closure.passport_no,
                })
                cand.flags.ignore_mandatory=True
                cand.db_update()
                frappe.db.commit()

        
def make_idb():
    date = add_months(today(),-3)
    project = frappe.db.sql("""select name from `tabProject` where dnd_onboarding_date < %s """,(date),as_dict=1)
    for pro in project:
        candidate = frappe.get_list('Candidate',{'project':pro.name,'pending_for':'Proposed PSL'})
        for cand in candidate:
            can = frappe.get_doc('Candidate',cand.name)
            can.pending_for = 'IDB'
            can.db_update()
        
@frappe.whitelist()
def send_ticket_request(name,recipient):
    clo = frappe.get_doc("Closure",name)
    recip=['sangeetha.s@voltechgroup.com',
            'sethusrinivasan.s@voltechgroup.com',
            'sahayasaji.s@voltechgroup.com',
            'divya.s@voltechgroup.com',
            'asha.j@voltechgroup.com',
            'sangeetha.j@voltechgroup.com',
            ]
    if recipient not in recip:
        recip.append(recipient)
    if clo.return_needed == 1:
        rn = "Yes"
    else:
        rn = "No"
    index = 1
    content = """<table class='table table-bordered'>
                <tr>
                <th>S.No</th>
                <th>Candidate Customer Name</th>
                <th>Given Name</th>
                <th>Sur Name or Father Name</th>
                <th>Date of Birth (DOB)</th>
                <th>Passport No</th>
                <th>Visa Type</th>
                <th>Date of Expiry (DOE) Visa</th>
                <th>Received Payment</th>
                <th>Pending Payment</th>
                <th>Date of Journey Requested</th>
                <th>DOJ Type</th>
                <th>Boarding Point</th>
                <th>Destination</th>
                <th>Return Needed</th>
                </tr>
                """
    details = """
        <tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        </tr>
    """%(index,clo.customer,clo.name1,clo.father_name,formatdate(clo.dob),clo.passport_no,clo.visa_type,formatdate(clo.visa_expiry_date),clo.candidate_advance,clo.candidate_pending,formatdate(clo.date_of_journey_requested),clo.doj_type,clo.boarding_point,clo.destination,rn)
    content += details
    frappe.sendmail(
        recipients= recip,
        subject='Candidate Ticket Request-Reg.',
        message="""
        <h3> Candidate Ticket Request</h3>
                <p>Dear Team,</p>
                <p>Kindly find below candidate details to book Air Ticket</p><br>
        %s"""%(content))
    return True


@frappe.whitelist()
def bulk_ticket_request(names):
    names = json.loads(names)
    # recip = 'subash.p@voltechgroup.com'
    recip=['sangeetha.s@voltechgroup.com',
            'sethusrinivasan.s@voltechgroup.com',
            'sahayasaji.s@voltechgroup.com',
            'divya.s@voltechgroup.com',
            'asha.j@voltechgroup.com',
            'sangeetha.j@voltechgroup.com',
            ]
    # if recipient not in recip:
    #     recip.append(recipient)
    index = 0
    content = """<table class='table table-bordered'>
                <tr>
                <th>S.No</th>
                <th>Candidate Customer Name</th>
                <th>Given Name</th>
                <th>Sur Name or Father Name</th>
                <th>Date of Birth (DOB)</th>
                <th>Passport No</th>
                <th>Visa Type</th>
                <th>Date of Expiry (DOE) Visa</th>
                <th>Received Payment</th>
                <th>Pending Payment</th>
                <th>Date of Journey Requested</th>
                <th>DOJ Type</th>
                <th>Boarding Point</th>
                <th>Destination</th>
                <th>Return Needed</th>
                </tr>
                """
    details = """<tr><td></td></tr>"""
    # status = []
    for name in names:
        clo = frappe.get_doc("Closure",name)
        # status.append(clo.status)
        index += 1
        if clo.return_needed == 1:
            rn = "Yes"
        else:
            rn = "No"
        details += """
            <tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            </tr>
        """%(index,clo.customer,clo.name1,clo.father_name,formatdate(clo.dob),clo.passport_no,clo.visa_type,formatdate(clo.visa_expiry_date),clo.candidate_advance,clo.candidate_pending,formatdate(clo.date_of_journey_requested),clo.doj_type,clo.boarding_point,clo.destination,rn)
    content += details
    # if status == "Ticket Details":
    frappe.sendmail(
        recipients= recip,
        subject='Candidate Ticket Request-Reg.',
        message="""
        <h3> Candidate Ticket Request</h3>
                <p>Dear Team,</p>
                <p>Kindly find below candidate details to book Air Ticket</p><br>
        %s"""%(content))
    frappe.msgprint("Ticket Request Sent")
    # else:
    #     frappe.throw("")

def mark_punch_time():
    days = ['2019-12-27','2019-12-28','2019-12-30','2019-12-31']
    for day in days:
    # day = add_day(today(),-1)
        query = """select employee,time,name from `tabEmployee Checkin` 
                    where date(time) = '%s' order by employee,time,name """ % day
        checkins = frappe.db.sql(query, as_dict=1)
        if checkins:
            for key, group in itertools.groupby(checkins, key=lambda x: (x['employee'])):
                logs = list(group)
                in_time = out_time = None
                in_time = logs[0].time
                employee = logs[0].employee
                if len(logs) >= 2:
                    out_time = logs[-1].time
                att_id = frappe.db.get_value("Attendance", {'employee': employee,"attendance_date":day,"branch":"Head Office - Chennai"})
                if in_time:
                    in_time = in_time.strftime("%H:%M:%S")
                if out_time:
                    out_time = out_time.strftime("%H:%M:%S")
                if att_id:
                    att = frappe.get_doc("Attendance", att_id)
                    att.in_time = in_time
                    att.out_time = out_time
                    att.db_update()
                    frappe.db.commit