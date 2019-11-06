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
from frappe.utils.csvutils import read_csv_content
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
# from netifaces import netifaces

@frappe.whitelist()
def bulk_update_closure():
    closure = ['TCR11262','TCR10932','TCR10931','TCR10930','TCR10929','TCR10925','TCR10924','TCR10923','TCR10922','TCR09754','TCR09723','TCR09737','TCR09749','TCR06108','TCR06102']
    for cl in closure:
        print cl
        frappe.db.set_value(
            "Closure",cl, "candidate_pending",flt("0"))

@frappe.whitelist()
def bulk_so_update():
    sales_order = frappe.db.sql("""
    select name,customer from `tabSales Order` where project = 'MECC_17/03/19' """, as_dict=1)
    for so in sales_order:
        sales_order = frappe.get_doc("Sales Order", so["name"])
        if not sales_order.docstatus == 2:
            sales_order.cancel()
            frappe.delete_doc("Sales Order",so["name"])

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
def so_from_import():
    closures = frappe.get_all("Closure",{'project':'MECC_17/03/19','status':('!=','Dropped')})
    for cl in closures:
        doc = frappe.get_doc("Closure",cl)
        name = doc.name
        customer = doc.customer
        project = doc.project
        name1 = doc.name1
        passport_no = doc.passport_no
        client_sc = doc.client_sc
        candidate_sc = doc.candidate_sc
        business_unit = doc.business_unit
        source_executive = doc.source_executive
        ca_executive = doc.ca_executive
        is_candidate = doc.candidate_payment_applicable
        is_client = doc.client_payment_applicable
        territory = frappe.db.get_value("Customer", customer, "territory")
        business_unit = frappe.get_value("Territory",territory,"business_unit")
        cg = frappe.db.get_value("Customer", customer, "customer_group")
        print passport_no,is_candidate,is_client
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
            if is_candidate and candidate_sc:
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
                    "item_code":passport_no,
                    "item_name": name1,
                    "payment_type": "Candidate",
                    "description": customer,
                    "uom": 'Nos',
                    "rate": candidate_sc,
                    "delivery_date": today()
                })
                so.insert()
                so.submit()
                so.save(ignore_permissions=True)

            if is_client:
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
                    "item_code":passport_no,
                    "item_name": name1,
                    "payment_type": "Client",
                    "description": customer,
                    "uom": 'Nos',
                    "rate": client_sc,
                    "delivery_date": today()
                })
                so.insert()
                so.submit()
                so.save(ignore_permissions=True)

@frappe.whitelist()
def delete_applicant_bvs():
    app_list = ["SIB-0130","SIB-0102","SIB-0116","SIB-0079","SIB-0077","SIB-0108","SIB-0107","SIB-0075","SIB-0111","SIB-0004","SIB-0126","SIB-0128","SIB-0127","SIB-0119","SIB-0125","SIB-0122","SIB-0124","SIB-0123","SIB-0121","SIB-0114","SIB-0120","SIB-0117","SIB-0115","SIB-0118","SIB-0113","SIB-0112","SIB-0109","SIB-0110","SIB-0105","SIB-0106","SIB-0103","SIB-0104","SIB-0101","SIB-0100","SIB-0099","SIB-0095","SIB-0096","SIB-0094","SIB-0093","SIB-0092","SIB-0091","SIB-0090","SIB-0088","SIB-0089","SIB-0087","SIB-0083","SIB-0084","SIB-0086","SIB-0085","SIB-0082","SIB-0081","SIB-0080","SIB-0076","SIB-0078","SIB-0073","SIB-0074","SIB-0072","SIB-0071","SIB-0070","SIB-0069","SIB-0068","SIB-0061","SIB-0067","SIB-0065","SIB-0066","SIB-0064","SIB-0063","SIB-0059","SIB-0057","SIB-0058","SIB-0055","SIB-0053","SIB-0054","SIB-0052","SIB-0050","SIB-0048","SIB-0049","SIB-0047","SIB-0023","SIB-0044","SIB-0043","SIB-0045","SIB-0046","SIB-0039","SIB-0042","SIB-0041","SIB-0040","SIB-0036","SIB-0037","SIB-0034","SIB-0038","SIB-0035","SIB-0032","SIB-0029","SIB-0033","SIB-0031","SIB-0030","SIB-0028","SIB-0027","SIB-0026","SIB-0025","SIB-0024","SIB-0022"]
    for a in app_list:
        # if frappe.db.exists("Verify Education Check1",{"applicant_id": a}):
        if frappe.db.exists("Education Check1",{"applicant_id": a}):
            # vedu1 = frappe.get_doc("Verify Education Check1",{"applicant_id": a})
            edu1 = frappe.get_doc("Education Check1",{"applicant_id": a})
            # frappe.delete_doc("Verify Education Check1",vedu1.name)
            frappe.delete_doc("Education Check1",edu1.name)
            frappe.errprint(edu1)

@frappe.whitelist()
def update_att():
    from_date = '2019-09-30'
    to_date = '2019-09-30'
    employee = frappe.db.sql("""select employee from `tabEmployee` where employment_type != 'Contract'""")
    # print employee
    for emp in employee:
        att = frappe.db.sql("""select in_time, out_time, employee,employee_name, attendance_date,name from `tabAttendance` where attendance_date between %s and %s and employee= %s """,(from_date,to_date,emp),as_dict=1)
        for at in att:
            print at.employee_name, at.in_time,at.out_time
            pr_id = frappe.db.exists("Punch Record",{"employee":at.employee,"attendance_date":at.attendance_date})
            times = []
            if pr_id:
                pr = frappe.get_doc("Punch Record",{"employee":at.employee,"attendance_date":at.attendance_date})
                for t in pr.timetable:
                    times.append(t.punch_time)
                in_time = min(times)
                out_time = max(times)
                if out_time == ' ':
                    out_time = ''
                if in_time == out_time:
                    out_time = ''
                attendance = frappe.get_doc("Attendance",at.name)
                if attendance:
                    attendance.in_time = in_time
                    attendance.out_time = out_time
                    attendance.db_update()
                    frappe.db.commit()
                else:
                    attendance = frappe.new_doc("Attendance")
                    attendance.in_time = in_time
                    attendance.out_time = out_time
                    attendance.db_update()
                    frappe.db.commit()
# @frappe.whitelist()
# def post_att(doc,method):
    

@frappe.whitelist()
def update_tasks():
    tasks = frappe.get_all("Task",filters={'status':("in",['Closed','Cancelled','Hold'])})
    for task in tasks:
        t = frappe.get_doc("Task",task)
        t.pending_profiles_to_send = 0
        t.db_update()
        frappe.db.commit()

    # tasks = frappe.get_all("Task",filters={'status':("not in",['Closed','Cancelled','Hold'])})
    # for task in tasks:
    #     t = frappe.get_doc("Task",task)
    #     candidates = t.candidates
    #     sourced = 0
    #     shortlisted = 0
    #     interviewed = 0
    #     proposed_psl = 0
    #     sourced = frappe.db.count('Candidate', {'task':t.name,'pending_for': ('in',['Sourced','Submitted'])})
    #     shortlisted = frappe.db.count('Candidate', {'task':t.name,'pending_for': 'Shortlisted'})
    #     interviewed = frappe.db.count('Candidate', {'task':t.name,'pending_for': 'Interviewed'})
    #     proposed_psl = frappe.db.count('Candidate', {'task':t.name,'pending_for': 'Proposed PSL'})
    #     t.r7_count = sourced
    #     t.r4_count = shortlisted
    #     t.r6_count = interviewed
    #     t.r3_count = proposed_psl
    #     if t.r1_count:
    #         if t.r3_count >= t.r1_count:
    #             t.pending_profiles_to_send = 0
    #         else: 
    #             vacancies = t.r1_count
    #             proposition = t.proposition
    #             pps = (vacancies - proposed_psl) * proposition - (sourced + shortlisted + interviewed)
    #             t.pending_profiles_to_send = pps
    #         t.db_update()
    #         frappe.db.commit()  

def bulk_update_from_csv(filename):
    #below is the method to get file from Frappe File manager
    from frappe.utils.file_manager import get_file
    #Method to fetch file using get_doc and stored as _file
    _file = frappe.get_doc("File", {"file_name": filename})
    #Path in the system
    filepath = get_file(filename)
    #CSV Content stored as pps

    pps = read_csv_content(filepath[1])
    for pp in pps:
        candidate = frappe.get_all("Candidate",{'project':pp[0]})
        for cand in candidate:
            can = frappe.get_doc('Candidate',cand.name)
            if can.pending_for != 'Proposed PSL':
                print can.pending_for
                # can.pending_for = "IDB"
                # can.db_update()
                # frappe.db.commit()
            
                                
# def customer_gst():
#     sales_invoice = frappe.get_all("Sales Invoice")
#     for si in sales_invoice:
#         sis = frappe.get_doc('Sales Invoice',si)
#         # print(sale.customer_address)
#         if frappe.db.exists("Address",{"address_title": sis.customer_address}):
#             address = frappe.get_doc('Address',{"address_title":sis.customer_address})
#             if address.gstin:
#                 # print(sis.customer_address)
#                 # print(address.gstin)
#                 sis.customer_gstin = address.gstin
#                 sis.db_update()
#                 frappe.db.commit()

def set_task_closed():
    tasks = frappe.get_all('Task',{'status':'Closed'},['project','name'])
    for task in tasks:
        frappe.db.set_value("Task",task['name'],"status","Completed")
        frappe.db.commit()

def update_op_status():
    projects = frappe.get_all('Project',filters={'operation_status':'Pending'})
    for project in projects:
        pro = frappe.get_doc('Project',project)
        if pro.status in ['Completed','Cancelled']:
            pro.operation_status = 'Completed'
            pro.db_update()
            frappe.db.commit()
        if pro.status == 'Hold':
            pro.operation_status = 'Hold'
            pro.db_update()
            frappe.db.commit()
        if pro.status == 'Open':    
            pro.operation_status = 'Sourcing'
            pro.db_update()
            frappe.db.commit()

def update_pro_status():
    projects = frappe.get_all('Project',fields={'name', 'status'},filters={'status':'Overdue'})
    print len(projects)
    comp = False
    for project in projects:
        tasks = frappe.db.get_all('Task',fields={'name', 'project', 'status'},filters={
            'project': project.name})
        # if tasks:
        #     if all(task.status == 'Completed' or task.status == 'Cancelled' for task in tasks):
        #         comp = True
        # if comp == True:
        #     pro = frappe.get_doc('Project',project.name)
        #     print pro.operation_status
        #     pro.status = 'Completed'
        #     pro.db_update()
        #     frappe.db.commit()

# def block_module():
#     user = frappe.get_all('',fields={'name', 'status'},filters={'status':'Overdue'})
def update_pm():
    # project = frappe.get_all("Project")
    # for p in project:
    #     pro = frappe.get_doc("Project",p)
    tasks = frappe.get_all("Task",{'status':("in",['Cancelled','Completed','Hold','DnD'])},['name','project','status'])
    for t in tasks:
        print t.status
        frappe.db.set_value("Task", t.name, "pending_profiles_to_send",'0')
        # frappe.db.set_value("Project", t.project, "pps",'0')
        # frappe.set_value("Task",t.name,"project_manager",pm)
        # if pm:
        #     t1 = frappe.get_doc("Task",t)
        #     t1.project_manager = pm
        #     t1.db_update()
        #     frappe.db.commit()

        # if not t1.project_manager:
        #     t1.project_manager = pro.project_manager
        #     t1.db_update()
    
        

          

