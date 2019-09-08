from __future__ import unicode_literals
import json
import calendar
import frappe
import socket
import os
import math
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils.data import today
from frappe.utils import time_diff_in_seconds, time_diff_in_hours, formatdate, add_months, cint, fmt_money, add_days
import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
import time
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee


@frappe.whitelist()
def send_absent_alert():
    day = date.today()
    att_ids = frappe.get_list('Attendance', filters={"docstatus": 0,
                                                     "attendance_date": day, "company": "Voltech HR Services Private Limited"})
    for att_id in att_ids:
        if not (att_id.in_time and att_id.out_time):
            att = frappe.get_doc("Attendance", att_id.name)
            recipients = frappe.get_value("Employee", att.employee, "user_id")
            # print att.employee, recipients
            frappe.sendmail(
                recipients=recipients,
                subject='Attendance Marked as Absent Alert for ' +
                formatdate(today()),
                message="""
                <h3> Attendance Marked as Absent</h3>
                <p>Dear %s,</p>
                <h4>Info:</h4>
                <p>Your attendance is marked as Absent.You are required to apply Leave or On Duty within 3 Days from today or else failing to do so it will be marked as LOP.</p><br> Regards <br>HR Team"""
                % (frappe.get_value("Employee", att.employee, "employee_name"))

            )


@frappe.whitelist()
def send_failed_punch_alert():
    day = date.today()
    # day = '2019-09-06'
    att_ids = frappe.get_list('Attendance', filters={
                              "docstatus": 1, "attendance_date": day, "company": "Voltech HR Services Private Limited"})
    for att_id in att_ids:
        att = frappe.get_doc("Attendance", att_id)
        if att.in_time and not att.out_time:
            recipients = frappe.get_value("Employee", att.employee, "user_id")
            # recipients = 'subash.p@voltechgroup.com'
            # print att.employee, recipients
            frappe.sendmail(
                recipients=recipients,
                subject='Missed Out Punch Alert ' +
                formatdate(today()),
                message="""
                <h3> Missed Out Punch Alert</h3>
                <p>Dear %s,</p>
                <h4>Info:</h4>
                <p>This is to intimate that today your In Time is recorded as  %s and there is no Out Time Recorded,So that attendance is marked as Absent.
                  You are required to apply Leave or On Duty within 3 Days from today or else failing to do so it will be marked as LOP.</p><br> Regards <br>HR Team"""
                % (frappe.get_value("Employee", att.employee, "employee_name"), att.in_time)
            )

@frappe.whitelist()
def speciallistquarterly():
    index = 0
    date_time = date.today()
    d = date_time.strftime("%B %Y")
    bday_list = frappe.db.sql("""select name,employee_name,business_unit,department,branch,designation,cug__number,original_date_of_birth from `tabEmployee` where month(original_date_of_birth) in (8,9,10)
        and employment_type != 'Contract' and status = 'Active' order by DAY(date_of_birth) ASC""", as_dict=1)
    doj_list = frappe.db.sql("""select name,employee_name,business_unit,department,branch,designation,cug__number,date_of_joining from `tabEmployee` where month(date_of_joining) in (8,9,10)
        and employment_type != 'Contract' and status = 'Active' order by DAY(date_of_joining) ASC""", as_dict=1)
    dom_list = frappe.db.sql("""select name,employee_name,business_unit,department,branch,designation,cug__number,date_of_marriage from `tabEmployee` where month(date_of_marriage) in (8,9,10)
        and employment_type != 'Contract' and status = 'Active' order by DAY(date_of_marriage) ASC""", as_dict=1)
    
    content = """<table class='table table-bordered'>
                <tr>
                <th>S.No</th>
                <th>Employee</th>
                <th>Employee Name</th>
                <th>Unit</th>
                <th>Department</th>
                <th>Branch</th>
                <th>Designation</th>
                <th>CUG</th>
                <th>Date</th>
                <th>Ordinal</th>
                </tr>
                """
    b_day = """<tr>
    <td colspan = "4" ><strong>Birthday List</strong></td></tr>
    <tr>"""
    doj_day = """<tr>
    <td colspan = "4" ><strong>Work Anniversary List</strong></td></tr>
    <tr>"""
    dom_day = """<tr>
    <td colspan = "4" ><strong>Wedding Anniversary List</strong></td></tr>
    <tr>"""
    if bday_list:
        for bday in bday_list:
            index += 1
            employee = bday.name
            employee_name = bday.employee_name
            business_unit = bday.business_unit
            department =bday.department
            branch = bday.branch
            designation =bday.designation
            cug = bday.cug__number
            age = calculate_exp(bday.original_date_of_birth)
            date_of_birth = str(bday.original_date_of_birth.strftime('%d/%m/%Y'))
            b_day += """
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
                </tr>
            """ % (index, employee, employee_name,business_unit,department,branch,designation,cug,date_of_birth,age)
        content += b_day
    if doj_list:
        index1 = 0
        for doj in doj_list:
            index1 += 1
            employee = doj.name
            employee_name = doj.employee_name
            business_unit = doj.business_unit
            department =doj.department
            branch = doj.branch
            designation =doj.designation
            cug = doj.cug__number,
            exp = calculate_exp(doj.date_of_joining)
            date_of_joining = str(doj.date_of_joining.strftime('%d/%m/%Y'))
            doj_day += """
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
                </tr>
            """ % (index1, employee, employee_name, business_unit,department,branch,designation,cug,date_of_joining,exp)
        content += doj_day
    if dom_list:
        index2 = 0
        for dom in dom_list:
            index2 += 1
            employee = dom.name
            employee_name = dom.employee_name
            business_unit = dom.business_unit
            department =dom.department
            branch = dom.branch
            designation =dom.designation
            cug = dom.cug__number,
            wed = calculate_exp(dom.date_of_marriage)
            date_of_marriage = str(dom.date_of_marriage.strftime('%d/%m/%Y'))
            dom_day += """
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
                </tr>
            """ % (index2, employee, employee_name, business_unit,department,branch,designation,cug,date_of_marriage,wed)
        content += dom_day + "</table>"
    frappe.sendmail(
        recipients=['abdulla.pi@voltechgroup.com','thamaraikannan.m@voltechgroup.com'],
        subject='Special Day List',
        message="""
        <p>Dear Sir,</p>
        <P> Please find the special Day list for this Month %s, %s""" % (d, content))


@frappe.whitelist()
def speciallist():
    index = 0
    date_time = date.today()
    d = date_time.strftime("%B %Y")
    bday_list = frappe.db.sql("""select name,employee_name,business_unit,department,branch,designation,cug__number,original_date_of_birth from `tabEmployee` where month(original_date_of_birth) = month(NOW())
        and employment_type != 'Contract' and status = 'Active' order by DAY(date_of_birth) ASC""", as_dict=1)
    doj_list = frappe.db.sql("""select name,employee_name,business_unit,department,branch,designation,cug__number,date_of_joining from `tabEmployee` where month(date_of_joining) = month(NOW())
        and employment_type != 'Contract' and status = 'Active' order by DAY(date_of_joining) ASC""", as_dict=1)
    dom_list = frappe.db.sql("""select name,employee_name,business_unit,department,branch,designation,cug__number,date_of_marriage from `tabEmployee` where month(date_of_marriage) = month(NOW())
        and employment_type != 'Contract' and status = 'Active' order by DAY(date_of_marriage) ASC""", as_dict=1)
    
    content = """<table class='table table-bordered'>
                <tr>
                <th>S.No</th>
                <th>Employee</th>
                <th>Employee Name</th>
                <th>Unit</th>
                <th>Department</th>
                <th>Branch</th>
                <th>Designation</th>
                <th>CUG</th>
                <th>Date</th>
                <th>Ordinal</th>
                </tr>
                """
    b_day = """<tr>
    <td colspan = "4" ><strong>Birthday List</strong></td></tr>
    <tr>"""
    doj_day = """<tr>
    <td colspan = "4" ><strong>Work Anniversary List</strong></td></tr>
    <tr>"""
    dom_day = """<tr>
    <td colspan = "4" ><strong>Wedding Anniversary List</strong></td></tr>
    <tr>"""
    if bday_list:
        for bday in bday_list:
            index += 1
            employee = bday.name
            employee_name = bday.employee_name
            business_unit = bday.business_unit
            department =bday.department
            branch = bday.branch
            designation =bday.designation
            cug = bday.cug__number
            age = calculate_exp(bday.original_date_of_birth)
            date_of_birth = str(bday.original_date_of_birth.strftime('%d/%m/%Y'))
            b_day += """
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
                </tr>
            """ % (index, employee, employee_name,business_unit,department,branch,designation,cug,date_of_birth,age)
        content += b_day
    if doj_list:
        index1 = 0
        for doj in doj_list:
            index1 += 1
            employee = doj.name
            employee_name = doj.employee_name
            business_unit = doj.business_unit
            department =doj.department
            branch = doj.branch
            designation =doj.designation
            cug = doj.cug__number,
            exp = calculate_exp(doj.date_of_joining)
            date_of_joining = str(doj.date_of_joining.strftime('%d/%m/%Y'))
            doj_day += """
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
                </tr>
            """ % (index1, employee, employee_name, business_unit,department,branch,designation,cug,date_of_joining,exp)
        content += doj_day
    if dom_list:
        index2 = 0
        for dom in dom_list:
            index2 += 1
            employee = dom.name
            employee_name = dom.employee_name
            business_unit = dom.business_unit
            department =dom.department
            branch = dom.branch
            designation =dom.designation
            cug = dom.cug__number,
            wed = calculate_exp(dom.date_of_marriage)
            date_of_marriage = str(dom.date_of_marriage.strftime('%d/%m/%Y'))
            dom_day += """
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
                </tr>
            """ % (index2, employee, employee_name, business_unit,department,branch,designation,cug,date_of_marriage,wed)
        content += dom_day + "</table>"
    frappe.sendmail(
        # recipients=['abdulla.pi@voltechgroup.com','thamaraikannan.m@voltechgroup.com'],
        recipients=['abdulla.pi@voltechgroup.com','dineshbabu.k@voltechgroup.com','m.lavanya@voltechgroup.com'],
        subject='Special Day List',
        message="""
        <p>Dear Sir,</p>
        <P> Please find the special Day list for this Month %s, %s""" % (d, content))

def calculate_exp(dtob):
    today = date.today()
    return today.year - dtob.year - ((today.month, today.day) < (dtob.month, dtob.day))

@frappe.whitelist()
def send_daily_report():
    day = today()
    att_hl_list = []
    employees = frappe.get_all('Employee', filters={"status": "Active"})
    for employee in employees:
        holiday_list = frappe.db.get_value(
            "Employee", {'employee': employee.name}, ['holiday_list'])
        holiday_date = frappe.db.get_all(
            "Holiday", filters={'holiday_date': day, 'parent': holiday_list})
        if holiday_date:
            att_hl_list += frappe.db.sql("""select name,employee,employee_name,business_unit from `tabEmployee` where status = 'Active'
            and employment_type != 'Contract' and company != 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL' and branch != 'Kovur' and employee='%s' """ % (employee.name), as_dict=1)

    att_pre_list = frappe.db.sql("""select name,employee,employee_name,business_unit,attendance_date,status,in_time,onduty_status,leave_type from `tabAttendance` where attendance_date = curdate()
    and status = 'Present' and company != 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL'and branch != 'Kovur' order by in_time DESC""", as_dict=1)
    att_abs_list = frappe.db.sql("""select name,employee,employee_name,business_unit,attendance_date,status,in_time,onduty_status,leave_type from `tabAttendance` where attendance_date = curdate()
    and status = 'Absent' and company != 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL' and branch != 'Kovur' order by in_time""", as_dict=1)
    att_hd_list = frappe.db.sql("""select name,employee,employee_name,business_unit,attendance_date,status,in_time,onduty_status,leave_type from `tabAttendance` where attendance_date = curdate()
    and status = 'Half Day' and company != 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL' and branch != 'Kovur' order by in_time DESC""", as_dict=1)
    att_ol_list = frappe.db.sql("""select name,employee,employee_name,business_unit,attendance_date,status,in_time,onduty_status,leave_type from `tabAttendance` where attendance_date = curdate()
    and status = 'On Leave' and company != 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL' and branch != 'Kovur' order by in_time""", as_dict=1)
    total = att_pre_list + att_abs_list + att_hl_list + att_hd_list + att_ol_list
    employee_count = len(total)
    pre_count = len(att_pre_list)
    abs_count = len(att_abs_list)
    hd_count = len(att_hd_list)
    ol_count = len(att_ol_list)
    hl_count = len(att_hl_list)
    content = """
             <h4>Dear Sir,</h4>
             <p>Kindly find the Attendance Report of %s Employees,</p>
             <ul><p><li><b>Present : </b>%s</li></p>
             <p><li><b>Absent : </b>%s</li></p>
             <p><li><b>Half day : </b>%s</li></p>
             <p><li><b>Holiday : </b>%s</li></p></ul><br>
              """ % (employee_count, pre_count, abs_count, hd_count, hl_count)
    content += """<table class='table table-bordered'>
                <tr>
                <th>S.No</th>
                <th>Employee</th>
                <th>Employee Name</th>
                <th>Attendance Date</th>
                <th>In Time</th>
                <th>Status</th>
                <th>OD Status</th>
                <th>Leave Type</th>
                </tr>
                """
    pre_list = """<tr>
    <td colspan = "8" ><strong>Present List</strong></td></tr>
    <tr>"""
    abs_list = """<tr>
    <td colspan = "8" ><strong>Absent List</strong></td></tr>
    <tr>"""
    hd_list = """<tr>
    <td colspan = "8" ><strong>Half Day List</strong></td></tr>
    <tr>"""
    ol_list = """<tr>
    <td colspan = "8" ><strong>On Leave List</strong></td></tr>
    <tr>"""
    hl_list1 = """<tr>
    <td colspan = "8" ><strong>Holiday List</strong></td></tr>
    <tr>"""
    if att_hl_list:
        index = 0
        status = "Holiday"
        for hl_list in att_hl_list:
            index += 1
            employee = hl_list.employee
            employee_name = hl_list.employee_name
            status = "Holiday"
            hl_list1 += """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td></td>
                <td></td>
                <td>%s</td>
                <td></td>
                <td></td>
            </tr>
            """ % (index, employee, employee_name,  status)
        content += hl_list1
    if att_ol_list:
        index = 0
        for l_list in att_ol_list:
            index += 1
            employee = l_list.employee
            employee_name = l_list.employee_name
            attendance_date = str(l_list.attendance_date.strftime('%d/%m/%Y'))
            in_time = l_list.in_time
            status = l_list.status
            onduty_status = l_list.onduty_status
            leave_type = l_list.leave_type
            ol_list += """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """ % (index, employee, employee_name, attendance_date, in_time, status, onduty_status, leave_type)
        content += ol_list
    if att_abs_list:
        index = 0
        for a_list in att_abs_list:
            index += 1
            employee = a_list.employee
            employee_name = a_list.employee_name
            attendance_date = str(a_list.attendance_date.strftime('%d/%m/%Y'))
            in_time = a_list.in_time
            status = a_list.status
            onduty_status = a_list.onduty_status
            leave_type = a_list.leave_type
            abs_list += """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """ % (index, employee, employee_name, attendance_date, in_time, status, onduty_status, leave_type)
        content += abs_list
    if att_hd_list:
        index = 0
        for h_list in att_hd_list:
            index += 1
            employee = h_list.employee
            employee_name = h_list.employee_name
            attendance_date = str(h_list.attendance_date.strftime('%d/%m/%Y'))
            in_time = h_list.in_time
            status = h_list.status
            onduty_status = h_list.onduty_status
            leave_type = h_list.leave_type
            hd_list += """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """ % (index, employee, employee_name, attendance_date, in_time, status, onduty_status, leave_type)
        content += hd_list
    if att_pre_list:
        index = 0
        for p_list in att_pre_list:
            index += 1
            employee = p_list.employee
            employee_name = p_list.employee_name
            attendance_date = str(p_list.attendance_date.strftime('%d/%m/%Y'))
            in_time = p_list.in_time
            status = p_list.status
            onduty_status = p_list.onduty_status
            leave_type = p_list.leave_type
            pre_list += """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """ % (index, employee, employee_name, attendance_date, in_time, status, onduty_status, leave_type)
        content += pre_list + "</table>"
    frappe.sendmail(
        recipients=[
            'dineshbabu.k@voltechgroup.com',
            'abdulla.pi@voltechgroup.com',
            
        ],
        subject='Employee Daily Attendance Report - ' +
        formatdate(today()),
        message=""" %s""" % (content))
    frappe.msgprint(content)


@frappe.whitelist()
def send_preday_report():
    att_hl_list = []
    day = add_days(today(), -1)
    # day = '2019-04-06'
    employees = frappe.get_all('Employee', filters={"status": "Active"})
    for employee in employees:
        holiday_list = frappe.db.get_value(
            "Employee", {'employee': employee.name}, ['holiday_list'])
        holiday_date = frappe.db.get_all(
            "Holiday", filters={'holiday_date': day, 'parent': holiday_list})
        if holiday_date:
            att_hl_list += frappe.db.sql("""select name,employee,employee_name,business_unit from `tabEmployee` where status = 'Active'
            and employment_type != 'Contract' and company != 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL' and branch != 'Kovur' and employee='%s' """ % (employee.name), as_dict=1)
        
    att_pre_list = frappe.db.sql("""select name,employee,employee_name,business_unit,attendance_date,status,in_time,onduty_status,leave_type from `tabAttendance` where status = 'Present'
    and company != 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL'and branch != 'Kovur' and attendance_date = %s order by in_time DESC""", (day), as_dict=1)
    att_abs_list = frappe.db.sql("""select name,employee,employee_name,business_unit,attendance_date,status,in_time,onduty_status,leave_type from `tabAttendance` where status = 'Absent'
    and company != 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL'and branch != 'Kovur' and attendance_date = %s order by in_time DESC""", (day), as_dict=1)
    att_hd_list = frappe.db.sql("""select name,employee,employee_name,business_unit,attendance_date,status,in_time,onduty_status,leave_type from `tabAttendance` where status = 'Half Day'
    and company != 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL'and branch != 'Kovur' and attendance_date = %s order by in_time DESC""", (day), as_dict=1)
    att_ol_list = frappe.db.sql("""select name,employee,employee_name,business_unit,attendance_date,status,in_time,onduty_status,leave_type from `tabAttendance` where status = 'On Leave'
    and company != 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL'and branch != 'Kovur' and attendance_date = %s order by in_time DESC""", (day), as_dict=1)
    hl_list1 = """<tr>
                <td colspan = "8" ><strong>Holiday List</strong></td></tr>
                <tr>"""
    pre_list = """<tr>
    <td colspan = "8" ><strong>Present List</strong></td></tr>
    <tr>"""
    abs_list = """<tr>
    <td colspan = "8" ><strong>Absent List</strong></td></tr>
    <tr>"""
    hd_list = """<tr>
    <td colspan = "8" ><strong>Half Day List</strong></td></tr>
    <tr>"""
    ol_list = """<tr>
    <td colspan = "8" ><strong>On Leave List</strong></td></tr>
    <tr>"""
    total = att_pre_list + att_abs_list + att_hl_list + att_hd_list + att_ol_list
    employee_count = len(total)
    pre_count = len(att_pre_list)
    abs_count = len(att_abs_list)
    hd_count = len(att_hd_list)
    ol_count = len(att_ol_list)
    hl_count = len(att_hl_list)
    content = """
             <h4>Dear Sir,</h4>
             <p>Kindly find the Yesterday Attendance Report of %s Employees,</p>
             <ul><p><li><b>Present : </b>%s</li></p>
             <p><li><b>Absent      : </b>%s</li></p>
             <p><li><b>Half day    : </b>%s</li></p>
             <p><li><b>Holiday     : </b>%s</li></p>
             <p><li><b>On Leave     : </b>%s</li></p>
             </ul><br>
              """ % (employee_count, pre_count, abs_count, hd_count, hl_count,ol_count)
    content += """<table class='table table-bordered'>
                <tr>
                <th>S.No</th>
                <th>Employee</th>
                <th>Employee Name</th>
                <th>Attendance Date</th>
                <th>In Time</th>
                <th>Status</th>
                <th>OD Status</th>
                <th>Leave Type</th>
                </tr>
                """

    if att_hl_list:
        index = 0
        for hl_list in att_hl_list:
            index += 1
            employee = hl_list.employee
            employee_name = hl_list.employee_name
            status = "Holiday"
            hl_list1 += """
                            <tr>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td></td>
                                <td>%s</td>
                                <td></td>
                                <td></td>
                                <td></td>
                            </tr>
                            """ % (index, employee, employee_name, status)
        content += hl_list1
        # print content
    if att_ol_list:
        index = 0
        for l_list in att_ol_list:
            index += 1
            employee = l_list.employee
            employee_name = l_list.employee_name
            attendance_date = str(l_list.attendance_date.strftime('%d/%m/%Y'))
            in_time = l_list.in_time
            status = l_list.status
            onduty_status = l_list.onduty_status
            leave_type = l_list.leave_type
            ol_list += """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """ % (index, employee, employee_name, attendance_date, in_time, status, onduty_status, leave_type)
        content += ol_list
    if att_abs_list:
        index = 0
        for a_list in att_abs_list:
            index += 1
            employee = a_list.employee
            employee_name = a_list.employee_name
            attendance_date = str(a_list.attendance_date.strftime('%d/%m/%Y'))
            in_time = a_list.in_time
            status = a_list.status
            onduty_status = a_list.onduty_status
            leave_type = a_list.leave_type
            abs_list += """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """ % (index, employee, employee_name, attendance_date, in_time, status, onduty_status, leave_type)
        content += abs_list
    if att_hd_list:
        index = 0
        for h_list in att_hd_list:
            index += 1
            employee = h_list.employee
            employee_name = h_list.employee_name
            attendance_date = str(h_list.attendance_date.strftime('%d/%m/%Y'))
            in_time = h_list.in_time
            status = h_list.status
            onduty_status = h_list.onduty_status
            leave_type = h_list.leave_type
            hd_list += """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """ % (index, employee, employee_name, attendance_date, in_time, status, onduty_status, leave_type)
        content += hd_list
    if att_pre_list:
        index = 0
        for p_list in att_pre_list:
            index += 1
            employee = p_list.employee
            employee_name = p_list.employee_name
            attendance_date = str(p_list.attendance_date.strftime('%d/%m/%Y'))
            in_time = p_list.in_time
            status = p_list.status
            onduty_status = p_list.onduty_status
            leave_type = p_list.leave_type
            pre_list += """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """ % (index, employee, employee_name, attendance_date, in_time, status, onduty_status, leave_type)
        content += pre_list + "</table>"
    frappe.sendmail(
        recipients=[
            'dineshbabu.k@voltechgroup.com',
            'abdulla.pi@voltechgroup.com',
            'm.lavanya@voltechgroup.com',
            'jobs@voltechgroup.com'
        ],
        subject='Employee Daily Attendance Report - ' +
        formatdate(add_days(today(), -1)),
        message=""" %s""" % (content))

@frappe.whitelist()
def absent_list_alert():
    day = today()
    att_hl_list = []
    employees = frappe.get_all('Employee', filters={"status": "Active"})
    for employee in employees:
        holiday_list = frappe.db.get_value(
            "Employee", {'employee': employee.name}, ['holiday_list'])
        holiday_date = frappe.db.get_all(
            "Holiday", filters={'holiday_date': day, 'parent': holiday_list})
        if holiday_date:
            att_hl_list += frappe.db.sql("""select name,employee,employee_name,business_unit from `tabEmployee` where status = 'Active'
            and employment_type != 'Contract' and company != 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL' and branch != 'Kovur' and employee='%s' """ % (employee.name), as_dict=1)

    att_abs_list = frappe.db.sql("""select name,employee,employee_name,business_unit,attendance_date,status,in_time,onduty_status,leave_type from `tabAttendance` where attendance_date = curdate()
    and status = 'Absent' and company != 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL' order by in_time""", as_dict=1)
    att_hd_list = frappe.db.sql("""select name,employee,employee_name,business_unit,attendance_date,status,in_time,onduty_status,leave_type from `tabAttendance` where attendance_date = curdate()
    and status = 'Half Day' and company != 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL' order by in_time DESC""", as_dict=1)

    abs_list = """<tr>
    <td colspan = "8" ><strong>Absent List</strong></td></tr>
    <tr>"""

    content = """
             <h4>Dear Team,</h4>
             <p>Below Employees are Marked as absent today,Those are required to apply Leave or On Duty within 3 Days or else failing to do so it will be marked as LOP.</p><br>"""
    content += """<table class='table table-bordered'>
                <tr>
                <th>S.No</th>
                <th>Employee</th>
                <th>Employee Name</th>
                <th>Attendance Date</th>
                <th>In Time</th>
                <th>Status</th>
                <th>OD Status</th>
                <th>Leave Type</th>
                </tr>
                """

    if att_abs_list:
        index = 0
        for a_list in att_abs_list:
            index += 1
            employee = a_list.employee
            employee_name = a_list.employee_name
            attendance_date = str(a_list.attendance_date.strftime('%d/%m/%Y'))
            in_time = a_list.in_time
            status = a_list.status
            onduty_status = a_list.onduty_status
            leave_type = a_list.leave_type
            abs_list += """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """ % (index, employee, employee_name, attendance_date, in_time, status, onduty_status, leave_type)
        content += abs_list

    frappe.sendmail(
        recipients=[
            # 'dineshbabu.k@voltechgroup.com',
            # 'abdulla.pi@voltechgroup.com',
            'vhrs_all@voltechgroup.com'
        ],
        subject='Employee Absent Alert - ' +
        formatdate(today()),
        message=""" %s""" % (content))
    frappe.msgprint(content)


@frappe.whitelist()
def closure_drop_alert():
    drop_list = frappe.db.sql(
        """select name1,passport_no,sales_order_confirmed_date,dropped_date,customer,candidate_sc,client_sc,dropped_date,project from `tabClosure` where `dropped_date` between date_sub(now(),interval 7 day) and now() and `sales_order_confirmed_date` is not null""", as_dict=1)
    # print drop_list
    content = """
             <h4>Dear Sir,</h4>
             <p>Kindly find the Dropped list for this week.</p><br>"""
    content += """<table class='table table-bordered'>
                <tr>
                <th>S.No</th>
                <th>Candidate Name</th>
                <th>PP No.</th>
                <th>Sales Order Confirmed Date</th>
                <th>Dropped Date</th>
                <th>Customer</th>
                <th>Project</th>
                <th>Candidate_SC</th>
                <th>Client_SC</th>
                </tr>
                """
    drop_l = """<tr>
    <td colspan = "4" ><strong>Dropped List</strong></td></tr>
    <tr>"""
    if drop_list:
        index = 0
        for drop in drop_list:
            # print drop.name1
            index += 1
            name1 = drop.name1
            pp_no = drop.passport_no
            sales_order_confirmed_date = drop.sales_order_confirmed_date
            dropped_date = drop.dropped_date
            customer = drop.customer
            project = drop.project
            candidate = drop.candidate_sc
            client = drop.client_sc

            drop_l += """
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
                </tr>
            """ % (index, name1,pp_no,sales_order_confirmed_date,dropped_date, customer, project, candidate, client)
            # print drop
        content += drop_l

    frappe.sendmail(
        recipients=[
            'Prabavathi.d@voltechgroup.com',
            'sethusrinivasan.s@voltechgroup.com',
            'sahayasaji.s@voltechgroup.com'
        ],
        subject='Closure Dropped List - ' +
        formatdate(today()),
        message=""" %s""" % (content))



@frappe.whitelist()
def id_card_request(name):
    emp = frappe.get_doc("Employee", name)
    # frappe.errprint(emp.department)
    content = """
             <h4>Dear Sir,</h4>
             <p>Find the ID-Card Details of New Joinee,</p><br>"""
    content += """<table class='table table-bordered'>
                <tr>
                <th>Name</th>
                <th>Short code</th>
                <th>Father's Name</th>
                <th>Role</th>
                <th>Department</th>
                <th>Designation</th>
                <th>Employee_Code</th>
                <th>Blood Group</th>
                <th>Date of Birth</th>
                <th>Contact Number</th>
                <th>Identification_mark</th>
                <th>Address</th>
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
                </tr>
            """ % (emp.employee_name, emp.short_code,emp.father_name,emp.role,emp.department,emp.designation,emp.name, emp.blood_group,emp.date_of_birth,emp.cug__number,emp.identification_mark,emp.permanent_address)
    content+= details
    frappe.sendmail(
        recipients=[
            'thamaraikannan.m@voltechgroup.com',
            'm.lavanya@voltechgroup.com',
            # 'subash.p@voltechgroup.com'
        ],
        subject='New Joinee ID-Card Details - ' +
        formatdate(today()),
        message=""" %s""" % (content))
    # frappe.msgprint(content)
    

@frappe.whitelist()
def client_sc_change(name):
    can=frappe.get_doc("Closure",name)
    # frappe.errprint(can.name1)
    content="""<h4>Dear Sir,</h4><br>
    <p>Client Service Changed for %s<p><br>
    <p>You can see it by clicking <a href= "%s">Open Closure</a></p>""" %(can.name1,frappe.utils.get_url_to_form("Closure",name))
    # frappe.sendmail(
    #     recipients=[
    #         'subash.p@voltechgroup.com',
    #         'sethusrinivasan.s@voltechgroup.com'
    #         ],
    #     subject='Client Service Charge change Alert - ' +
    #     formatdate(today()),
    #     message=""" %s""" % (content))
    # frappe.msgprint(content)
    
@frappe.whitelist()
def candidate_sc_change(name):
    can=frappe.get_doc("Closure",name)
    # frappe.errprint(can.name1)
    content="""<h4>Dear Sir,</h4><br>
    <p>Candidate Service Changed for %s<p><br>
    <p>You can see it by clicking <a href= "%s">Open Closure</a></p>""" %(can.name1,frappe.utils.get_url_to_form("Closure",name))
    # frappe.sendmail(
    #     recipients=[
    #         'subash.p@voltechgroup.com',
    #         'sethusrinivasan.s@voltechgroup.com'
    #         ],
    #     subject='Candidate Service Charge change Alert - ' +
    #     formatdate(today()),
    #     message=""" %s""" % (content))
    # frappe.msgprint(content)

@frappe.whitelist()
def send_revenue_margin(project):
    pro = frappe.get_doc("Project",project)
    eipc = fmt_money(pro.expected_income_per_candidate,0,currency='INR')
    epc = fmt_money(pro.expected_expenses_per_candidate,0,currency='INR')
    etc = fmt_money(pro.expected_total_revenue,0,currency='INR')
    tefe = fmt_money(pro.total_expected_fixed_expenses,0,currency='INR')
    teve = fmt_money(pro.expected_total_variable_expenses,0,currency='INR')
    tpee = fmt_money(pro.total_project_expenses_expected,0,currency='INR')
    rm = fmt_money(pro.revenue_margin,0,currency='INR')
    rmp = round(pro.revenue_margin_percentage,2)
   
    # frappe.errprint(pro.expected_number_of_closures)

    content = """
             <h4>Dear Sir ,</h4>
             <h4>Kindly find the below FFA pending for your approval</h4>
             <p></p><br>"""
    content += """<table class='table table-bordered'>
                <tr>
                <th>Project Name</th><td>%s</td>
                <th>Project Incharge</th><td>%s</td>
                <th>Mode of Interview</th><td>%s</td>
                
                </tr>
            <tr>
                <th>Total No.of vacancies</th><td>%s</td>
                <th>Expected No.of Closures(X)</th><td>%s</td>
                <th>Expected Income per Candidate(Y) </th><td>%s</td>
                
                </tr>
            <tr>    
                <th>Expected Expenses per Candidate(Z) </th><td>%s</td>
                <th>Expected Total Revenue(X*Y)</th><td>%s</td>
                <th>Total Expected Fixed Expenses(R)</th><td>%s</td>
                
                </tr>
            <tr>  
                <th>Expected Total Variable Expenses(X*Z)</th><td>%s</td>
                <th>Total Project Expenses Expected(R+Q)</th><td>%s</td>  
                <th>Revenue Margin(P-S)</th><td>%s</td>
                </tr>
            <tr>    
                <th>Revenue Margin Percentage</th><td>%s %%</td>
            </tr>      
            </table>    
                <p>You can Acknowledge by clicking the below Link </p>
<a href="%s">Acknowldge FFA</a>
            """ % (pro.project_name,pro.cpc,pro.mode_of_interview,pro.total_number_of_vacancies,pro.expected_number_of_closures,eipc,epc,etc,tefe,teve,tpee,rm,rmp,frappe.utils.get_url_to_form("Project", pro.project_name))
                
    bu = frappe.get_value("Project",pro.project_name,'business_unit')
    if bu == 'BUHR-1':
        cc=['sangeetha.s@voltechgroup.com',
            'sangeetha.a@voltechgroup.com',
            'dineshbabu.k@voltechgroup.com'
        ]
    if bu == 'BUHR-2':
        cc=['jagan.k@voltechgroup.com',
            'dhavachelvan.d@voltechgroup.com',
            'dineshbabu.k@voltechgroup.com'
        ]
    frappe.sendmail(
        # recipients=['abdulla.pi@voltechgroup.com'],
        recipients=['sethusrinivasan.s@voltechgroup.com'],
        cc=cc,
        subject='Application for FFA',
        message=content)
    # frappe.msgprint(content)
    
