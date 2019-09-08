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
def update_autopresent():
    day = date.today()
    employees = frappe.get_all(
        'Employee', filters={"status": "Active", "branch": ("in", ("Qatar", "UAE", "Oman", "Kuwait"))})
    for employee in employees:
        holiday_list = frappe.db.get_value(
            "Employee", {'employee': employee.name}, ['holiday_list'])
        holiday_date = frappe.db.get_all(
            "Holiday", filters={'holiday_date': day, 'parent': holiday_list})
        if holiday_date:
            pass
        else:
            att = frappe.new_doc("Attendance")
            emp = frappe.get_doc("Employee", employee.name)
            att.update({
                "employee": emp.employee,
                "employee_name": emp.employee_name,
                "attendance_date": day,
                "company": emp.company,
                "business_unit": emp.business_unit,
                "status": "Present",
                "in_time": "",
                "out_time": "",
                "branch": emp.branch,
                "shift": emp.shift,
                "total_working_hour": ""
            })
            att.save(ignore_permissions=True)
            att.submit()
            frappe.db.commit()


@frappe.whitelist()
def mark_absent_a():
    try:
        day = date.today()
        employees = frappe.get_all(
            'Employee', filters={"shift": "A", "status": "Active", "company": ("!=", 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL'),"employment_type":("!=","Contract")})
        
        for employee in employees:
            status = check_record(employee.name, day)
            holiday_list = frappe.db.get_value(
                "Employee", {'employee': employee.name}, ['holiday_list'])
            holiday_date = frappe.db.get_all(
                "Holiday", filters={'holiday_date': day, 'parent': holiday_list})
            if holiday_date:
                pass
            else:
                att = frappe.new_doc("Attendance")
                emp = frappe.get_doc("Employee", employee.name)
                att_id = frappe.db.exists("Attendance", {
                    "employee": employee.name, "status": ("`in", ("Present", "On Leave")), "attendance_date": day})
                if att_id:
                    pass
                elif status == "On Leave" or status == "Half Day":
                    att.update({
                        "employee": emp.employee,
                        "employee_name": emp.employee_name,
                        "attendance_date": day,
                        "status": status,
                        "company": emp.company,
                        "business_unit": emp.business_unit
                    })
                    att.submit()
                    frappe.db.commit()
                elif status == "On Duty":
                    att.update({
                        "employee": emp.employee,
                        "employee_name": emp.employee_name,
                        "attendance_date": day,
                        "status": "Present",
                        "company": emp.company,
                        "business_unit": emp.business_unit,
                        "onduty_status": emp.onduty_status
                    })
                    att.submit()
                    frappe.db.commit()
                else:
                    att.update({
                        "employee": emp.employee,
                        "employee_name": emp.employee_name,
                        "attendance_date": day,
                        "status": "Absent",
                        "company": emp.company,
                        "business_unit": emp.business_unit
                    })
                    # print emp.employee_name
                    log_error("Mark Absent", emp.employee)
                    att.save(ignore_permissions=True)
                    frappe.db.commit()
    except requests.exceptions.ConnectionError as e:
        log_error("Connection Error", e)


def log_error(method, message):
    # employee = message["userid"]
    message = frappe.utils.cstr(message) + "\n" if message else ""
    d = frappe.new_doc("Error Log")
    d.method = method
    d.error = message
    d.insert(ignore_permissions=True)


@frappe.whitelist()
def mark_absent_g():
    try:
        day = date.today()
        employees = frappe.get_all(
            'Employee', filters={"shift": "G", "status": "Active", "company": ("!=", 'VOLTECH HUMAN RESOURCE PVT. LTD. NEPAL'),"employment_type":("!=","Contract")})
        print employees
        for employee in employees:
            status = check_record(employee.name, day)
            holiday_list = frappe.db.get_value(
                "Employee", {'employee': employee.name}, ['holiday_list'])
            holiday_date = frappe.db.get_all(
                "Holiday", filters={'holiday_date': day, 'parent': holiday_list})
            if holiday_date:
                pass
            else:
                emp = frappe.get_doc("Employee", employee.name)
                att_id = frappe.db.exists("Attendance", {
                    "employee": employee.name, "status": ("in", ("Present", "On Leave", "Half Day")), "attendance_date": day})
                if att_id:
                    pass
                else:
                    att = frappe.new_doc("Attendance")
                    if status == "On Leave" or status == "Half Day":
                        att.update({
                            "employee": emp.employee,
                            "employee_name": emp.employee_name,
                            "attendance_date": day,
                            "status": status,
                            "company": emp.company,
                            "business_unit": emp.business_unit
                        })
                        att.submit()
                        frappe.db.commit()
                    elif status == "On Duty":
                        att.update({
                            "employee": emp.employee,
                            "employee_name": emp.employee_name,
                            "attendance_date": day,
                            "status": "Present",
                            "company": emp.company,
                            "business_unit": emp.business_unit,
                            "onduty_status": status
                        })
                        att.submit()
                        frappe.db.commit()
                    else:
                        att.update({
                            "employee": emp.employee,
                            "employee_name": emp.employee_name,
                            "attendance_date": day,
                            "status": "Absent",
                            "company": emp.company,
                            "business_unit": emp.business_unit
                        })
                        # print emp.employee_name
                        log_error("Mark Absent", emp.employee)
                        att.save(ignore_permissions=True)
                        frappe.db.commit()
    except requests.exceptions.ConnectionError as e:
        log_error("Connection Error", e)


def log_error(method, message):
    # employee = message["userid"]
    message = frappe.utils.cstr(message) + "\n" if message else ""
    d = frappe.new_doc("Error Log")
    d.method = method
    d.error = message
    d.insert(ignore_permissions=True)


@frappe.whitelist()
def check_record(employee, day):
    status = ""
    leave_record = frappe.db.sql("""select leave_type, half_day from `tabLeave Application`
    where employee = %s and %s between from_date and to_date and status = 'Approved'
    and docstatus = 1""", (employee, day), as_dict=True)
    if leave_record:
        if leave_record[0].half_day:
            status = 'Half Day'
        else:
            status = 'On Leave'
            leave_type = leave_record[0].leave_type
        return status
    od_record = frappe.db.sql("""select employee, half_day from `tabOn Duty Application`
    where employee = %s and %s between from_date and to_date and status = 'Approved'
    and docstatus = 1""", (employee, day), as_dict=True)
    if od_record:
        status = 'On Duty'
        return status


@frappe.whitelist()
def update_att_a():
    day = today()
    att_ids = frappe.get_list('Attendance', filters={"shift": "A",
                                                     "docstatus": 0, "attendance_date": day})
    for att_id in att_ids:
        if att_id:
            att = frappe.get_doc("Attendance", att_id)
            if att and att.in_time:
                in_time_f = datetime.strptime(
                    att.in_time, '%H:%M:%S')
                in_time = in_time_f.strftime("%H:%M:%S")
                if in_time >= '07:45:00' and in_time <= '09:45:00':
                    status = check_permission(
                        att.employee, att.attendance_date, att.in_time)
                    if status:
                        att.update({
                            "status": "Present",
                            "permission_status": status
                        })
                        att.save(ignore_permissions=True)
                        att.submit()
                        frappe.db.commit()


@frappe.whitelist()
def update_att_g():
    day = date.today()
    att_ids = frappe.get_list('Attendance', filters={"shift": "G",
                                                     "docstatus": 0, "attendance_date": day})
    # print att_ids
    for att_id in att_ids:
        if att_id:
            shift_in_time = frappe.get_value("Shift","G","in_time") + frappe.get_value("Shift","G","grace_time")
            shift_max_time = frappe.get_value("Shift","G","max_permission_time")
            att = frappe.get_doc("Attendance", att_id)
            if att and att.in_time:
                in_time_f = datetime.strptime(
                    att.in_time, '%H:%M:%S')
                in_time = timedelta(hours=in_time_f.hour, minutes=in_time_f.minute, seconds=in_time_f.second)
                # in_time = in_time_f.strftime("%H:%M:%S")
                if(in_time < shift_in_time):
                    att.update(
                        {
                            "status": "Present"
                        }
                    )
                    att.save(ignore_permissions=True)
                    att.submit()
                    frappe.db.commit()

                if in_time >= shift_in_time and in_time <= shift_max_time:
                    status = check_permission(
                        att.employee, att.attendance_date, att.in_time)
                    if status:
                        att.update({
                            "status": "Present",
                            "permission_status": status
                        })
                        att.save(ignore_permissions=True)
                        att.submit()
                        frappe.db.commit()


def check_permission(employee, attendance_date, in_time):
    # Check if employee on On-Duty
    status = ""
    mark_permission(employee, attendance_date)

    start_date = get_first_day(attendance_date)
    end_date = get_last_day(attendance_date)
    mp = frappe.db.sql("""select count(*) as count  from `tabAttendance Permission` where employee = %s and docstatus != 2 and permission_date between %s and %s """,
                       (employee, start_date, end_date), as_dict=True)
    p_count = 0
    for p in mp:
        p_count = p.count
    if p_count <= 3:
        status = "Present"
    elif p_count == 4:
        status = "Half Day"
    elif p_count in range(4, 7):
        status = "Present"
    elif p_count == 7:
        status = "Half Day"
    elif p_count in range(7, 10):
        status = "Present"
    elif p_count == 10:
        status = "Half Day"
    elif p_count in range(10, 13):
        status = "Present"
    elif p_count in range(12, 19):
        status = "Half Day"
    elif p_count in range(18, 32):
        status = "Absent"

    # send_permission_alert(employee, attendance_date, in_time, p_count, status)
    return status


def mark_permission(emp, att_date):
    emp = frappe.get_doc("Employee", emp)
    attendance_permission = frappe.new_doc("Attendance Permission")
    attendance_permission.employee = emp.employee
    attendance_permission.employee_name = emp.employee_name
    attendance_permission.permission_date = att_date
    attendance_permission.department = emp.department
    attendance_permission.company = emp.company
    attendance_permission.save(ignore_permissions=True)
    attendance_permission.submit()
    frappe.db.commit()
    return True

def run_permission():
    # day = date.today()
    day = '2019-08-21'
    att_ids = frappe.get_list('Attendance', filters={
        "docstatus": ('!=', 2), "attendance_date": day})
    for att_id in att_ids:
        if att_id:
            att = frappe.get_doc("Attendance", att_id)
            if att.in_time and att.out_time:
                in_time_f = datetime.strptime(
                        att.in_time, '%H:%M:%S')
                out_time_f = datetime.strptime(
                    att.out_time, '%H:%M:%S')
                worked_hrs = out_time_f - in_time_f
                working_hrs = str(worked_hrs)
                total_working_hour = datetime.strptime(
                    working_hrs, '%H:%M:%S')
                total_working_hours = total_working_hour.strftime('%H:%M:%S')
                # print att.employee_name, total_working_hours
                # print total_working_hours
                hours=timedelta(hours=total_working_hour.hour, minutes=total_working_hour.minute, seconds=total_working_hour.second)
                f_max = timedelta(hours = 9.5)
                p_max = timedelta(hours = 8.5)
                cp_max = timedelta(hours = 8)
                h_max = timedelta(hours =5)
                # if att.shift == "C":
                #     c_max = timedelta(hours = 9)
                #     if hours <= c_max and hours >= cp_max:
                #         status = "Present"
                    # elif hours >= h_max:
                    #     status = "Half Day"
                    # else:
                    #     status = "Absent"
                        # print hours,att.employee_name
                        # att.update({
                        # "total_working_hour": total_working_hours,
                        # "status": status
                        # })
                        # att.db_update()
                        # frappe.db.commit()
                if att.shift == "A":
                    a_max = timedelta(hours = 8)
                    ap_max = timedelta(hours = 7)
                    if hours <= a_max and hours >= ap_max:
                        status = "Present"
                        print hours,att.employee_name,status
                    elif hours >= ap_max:
                        status = "Half Day"
                    else:
                        status = "Absent"
                        
                        per = mark_permission(att.employee,day)
                        att.update({
                        "total_working_hour": total_working_hours,
                        "status": status
                        })
                        att.db_update()
                        frappe.db.commit()
                # elif att.status == "On Duty":
                #     pass
                # elif hours <= f_max and hours >= p_max:
                    # print att.employee_name,hours
                    # per = mark_permission(att.employee,day)
                    # status = "Present"
                    # print att.employee_name,hours,status
                # elif hours >= p_max:
                #     status = "Half Day"
                # else:
                #     status = "Absent"
                    # att.update({
                    #     "total_working_hour": total_working_hours,
                    #     "status": status
                    # })
                    # att.db_update()
                    # frappe.db.commit()
                
def per_count():
    # employees = frappe.db.sql("""select name from `tabEmployee`
    #             where status = "Active" and  employment_type != "Contract" and company = "Voltech HR Services Private Limited" """, as_dict=True)
    # for emp in employees:
    per_count = frappe.db.sql("""select count(*) as count,employee from `tabAttendance Permission` where permission_date between "2019-08-01" and "2019-08-31" group by employee """,as_dict=1)
    for per in per_count:
        print per.employee, per.count

def get_first_day(dt, d_years=0, d_months=0):
    # d_years, d_months are "deltas" to apply to dt
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m - 1, 12)
    return date(y + a, m + 1, 1)


def get_last_day(dt):
    return get_first_day(dt, 0, 1) + timedelta(-1)


def validate_if_attendance_not_applicable(employee, attendance_date):
    # Check if attendance_date is a Holiday
    if is_holiday(employee, attendance_date):
        return "holiday", True
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
def send_permission_alert(employee, attendance_date, in_time, p_count, status):
    recipients = frappe.get_value("Employee", employee, "user_id")
    frappe.sendmail(
        recipients=recipients,
        subject='Attendance Marked as Permission Alert for ' +
        formatdate(today()),
        message="""
        <h3> Attendance Marked as Permission</h3>
        <p>Dear %s,</p>
        <h4>Info:</h4>
        <p>Your attendance is marked as %s and your In Time is %s .You are permission count for this month is %s.</p><br> Regards <br>HR Team"""
        % (frappe.get_value("Employee", employee, "employee_name"), status, in_time, p_count)

    )
    return True


@frappe.whitelist()
def update_attendance():
    day = date.today()
    att_ids = frappe.get_list('Attendance', filters={
        "docstatus": ('!=', 2), "attendance_date": day})
    for att_id in att_ids:
        if att_id:
            att = frappe.get_doc("Attendance", att_id)
            if att.in_time and not att.out_time:
                att.update({
                    "status": "Absent",
                    "in_time": "",
                    "docstatus": 0
                })
                att.db_update()
                frappe.db.commit()


@frappe.whitelist()
def total_working_hours():
    # day = date.today()
    day = '2019-08-21'
    total_working_hours = 0
    worked_hrs = 0
    att_ids = frappe.get_all('Attendance', filters={"attendance_date": day, "company": "Voltech HR Services Private Limited", "business_unit": ('!=', 'BUHR-4')})
    for att_id in att_ids:
        # print att_id
        if att_id:
            att = frappe.get_doc("Attendance", att_id)
            if att.in_time and not att.out_time:
                att.update({
                    "total_working_hour": "",
                    "status": "Absent"
                })
                att.db_update()
                frappe.db.commit()
            elif att.in_time and att.out_time:
                in_time_f = datetime.strptime(
                    att.in_time, '%H:%M:%S')
                out_time_f = datetime.strptime(
                    att.out_time, '%H:%M:%S')
                worked_hrs = out_time_f - in_time_f
                working_hrs = str(worked_hrs)
                total_working_hour = datetime.strptime(
                    working_hrs, '%H:%M:%S')
                total_working_hours = total_working_hour.strftime('%H:%M:%S')
                # print att.employee_name, total_working_hours
                # print total_working_hours
                hours=timedelta(hours=total_working_hour.hour, minutes=total_working_hour.minute, seconds=total_working_hour.second)
                f_max = timedelta(hours = 9.5)
                h_max = timedelta(hours =5)
                # if att.shift == "C":
                #     c_max = timedelta(hours = 9)
                #     if hours >= c_max:
                #         status = "Present"
                #     elif hours >= h_max:
                #         status = "Half Day"
                #     else:
                #         status = "Absent"
                if att.shift == "A":
                    a_max = timedelta(hours = 8)
                    b_max = timedelta(hours = 4)
                    print hours,a_max
                    if hours >= a_max:
                        status = "Present"
                    elif hours >= b_max:
                        status = "Half Day"
                    else:
                        status = "Absent"
                # elif att.status == "On Duty":
                #     pass
                # elif hours >= f_max:
                #     status = "Present"
                # elif hours >= h_max:
                #     status = "Half Day"
                # else:
                #     status = "Absent"
                
                # att.update({
                #     "total_working_hour": total_working_hours,
                #     "status": status
                # })
                # att.db_update()
                # frappe.db.commit()
            


@frappe.whitelist()
def mark_hd():
    day = date.today()
    att_ids = frappe.get_all('Attendance', filters={
        "docstatus": 0, "attendance_date": day})
    for att_id in att_ids:
        if att_id:
            att = frappe.get_doc("Attendance", att_id)
            if att.status == "Absent" and att.in_time:
                in_time_f = datetime.strptime(
                    att.in_time, '%H:%M:%S')
                in_time = in_time_f.strftime("%H:%M:%S")
                if in_time > '11:00:00' and in_time <= '14:00:00':
                    att.update({
                        "status": "Half Day"
                    })
                    att.save(ignore_permissions=True)
                    att.submit()
                    frappe.db.commit()
                elif in_time > '14:00:00':
                    att.update({
                        "status": "Absent"
                    })
                    att.save(ignore_permissions=True)
                    att.submit()
                    frappe.db.commit()


@frappe.whitelist()
def half_day():
    day = date.today()
    # day = '2019-02-20'
    total_working_hours = 0
    worked_hrs = 0
    working_hrs = 0
    att_ids = frappe.get_all('Attendance', filters={"docstatus": ('!=', 2),
                                                    "attendance_date": day, "company": "Voltech HR Services Private Limited", "business_unit": ('!=', 'BUHR-4')})
    for att_id in att_ids:
        if att_id:
            att = frappe.get_doc("Attendance", att_id)
            if att.in_time and att.out_time:
                in_time_f = datetime.strptime(
                    att.in_time, '%H:%M:%S')
                out_time_f = datetime.strptime(
                    att.out_time, '%H:%M:%S')
                actual_working_hours = frappe.db.get_value(
                    "Employee", att.employee, "working_hours")
                a_max_time = timedelta(hours=9, minutes=30)
                b_max_time = timedelta(hours=7, minutes=30)
                c_max_time = timedelta(hours=5)
                if att.total_working_hour >= a_max_time:
                    pass
                elif att.total_working_hour >= b_max_time and att.total_working_hour < a_max_time:
                    status = check_permission(
                        att.employee, att.attendance_date, att.in_time)
                    if status:
                        att.update({
                            "total_working_hour": total_working_hours
                        })
                        att.db_update()
                        frappe.db.commit()
                elif att.total_working_hour >= c_max_time and att.total_working_hour < b_max_time:
                    att.update({
                        "status": "Half Day"
                    })
                    att.db_update()
                    frappe.db.commit()
                else:
                    att.update({
                        "status": "Absent"
                    })
                    att.db_update()
                    frappe.db.commit()


# @frappe.whitelist()
# def mark_comp_off():
#     day = datetime.strptime(add_days(today(),-1), "%Y-%m-%d").date()
#     # day = date.today()
#     from_date = add_days(day, -1)
#     to_date = add_months(day, 12)
#     # print day
#     att_ids = frappe.get_list('Attendance', {"docstatus" : 2, "attendance_date": day, "company": "Voltech HR Services Private Limited"})
#     for att_id in att_ids:
#         # print att_id
#         if att_id:
#             # datetime.strptime(add_days(datetime.strptime(add_days(today(),-1), "%Y-%m-%d").date()today(),-1), "%Y-%m-%d").date()
#             new_leaves_allocated = 0
#             att = frappe.get_doc("Attendance", att_id)
#             # print att.in_time
#             if att.in_time and att.out_time:
#                 # print att_id
#                 holiday_list = frappe.db.get_value(
#                     "Employee", {'employee': att.employee}, ['holiday_list'])
#                 holiday_date = frappe.db.get_value(
#                     "Holiday", {'holiday_date': day, 'parent': holiday_list}, ["holiday_date"])
#                 a_max_time = timedelta(hours=9, minutes=30)
#                 b_max_time = timedelta(hours=5)
                
#                 if att and att.total_working_hour >= b_max_time:
#                     if att.total_working_hour >= b_max_time and att.total_working_hour < a_max_time:
#                         new_leaves_allocated = 0.5
#                     if att.total_working_hour >= a_max_time:
#                         new_leaves_allocated = 1
#                     lal_ids = get_lal(att.employee, holiday_date)
                    # print day
                    # print att.employee
                    # if lal_ids:
                    #     for lal_id in lal_ids:
                    #         lal = frappe.get_doc(
                    #             "Leave Allocation", lal_id['name'])
                    #         lal.new_leaves_allocated += new_leaves_allocated
                    #         lal.total_leaves_allocated += new_leaves_allocated
                    #         if lal.description:
                    #             lal.description += '<br>' + \
                    #                 'Comp-off for {0}'.format(day)
                    #         else:
                    #             lal.description = '<br>' + \
                    #                 'Comp-off for {0}'.format(day)
                    #         lal.db_update()
                    #         frappe.db.commit
                    # else:
                    #     lal = frappe.new_doc("Leave Allocation")
                    #     lal.employee = att.employee
                    #     lal.leave_type = 'Compensatory Off'
                    #     lal.from_date = day
                    #     lal.to_date = to_date
                    #     lal.new_leaves_allocated = new_leaves_allocated
                    #     lal.description = 'Comp-off for {0}'.format(day)
                    #     lal.save(ignore_permissions=True)
                    #     lal.submit()
                    #     frappe.db.commit()
@frappe.whitelist()
def mark_comp_off_new():
    day = datetime.strptime(add_days(today(),-1), "%Y-%m-%d").date()
    day = "2019-06-30"
    
    from_date = add_days(day, -1)
    to_date = add_months(day, 3)
    valid_till = add_months(day, 3)
    att_ids = frappe.get_list('Attendance', {"docstatus" : 2, "attendance_date": day, "company": "Voltech HR Services Private Limited"})
    for att_id in att_ids:
        if att_id:
            new_leaves_allocated = 0
            att = frappe.get_doc("Attendance", att_id)
            # print att.employee_name,att.in_time, att.out_time
            if att.in_time and att.out_time:
                # print att_id
                holiday_list = frappe.db.get_value(
                    "Employee", {'employee': att.employee}, ['holiday_list'])
                holiday_date = frappe.db.get_value(
                    "Holiday", {'holiday_date': day, 'parent': holiday_list}, ["holiday_date"])
                a_max_time = timedelta(hours=9, minutes=30)
                b_max_time = timedelta(hours=5)
                
                if att.total_working_hour >= b_max_time and att.total_working_hour < a_max_time:
                    new_leaves_allocated = 0.5
                if att.total_working_hour >= a_max_time:
                    new_leaves_allocated = 1
                # print att.total_working_hour, att.employee_name, new_leaves_allocated
                lal_ids = get_lal(att.employee, holiday_date)
                # print(lal_ids)
                # print day
                # print att.employee
                if frappe.db.exists("Leave Allocation",{"employee":att.employee,"leave_type":"Compensatory Off","to_date":to_date}):
                    pass
                
                else: 
                    lal = frappe.new_doc("Leave Allocation")
                    lal.description = 'Comp-off for {0}'.format(day)
                   
                    lal.employee = att.employee
                    lal.leave_type = 'Compensatory Off'
                    lal.from_date = day
                    lal.compensatory_off_date = day
                    lal.to_date = to_date
                    lal.valid_till = valid_till
                    lal.new_leaves_allocated = new_leaves_allocated
                    lal.save(ignore_permissions=True)
                    # print day,to_date,valid_till
                    lal.submit()
                    frappe.db.commit()

def delete_comp_off():
    # day = datetime.strptime(add_days(today(),1), "%Y-%m-%d").date()
    lev_all = frappe.db.sql("""select name from `tabLeave Allocation` where valid_till = %s""",(day),as_dict=True)
    print lev_all
    for lev in lev_all:
        comp = frappe.get_doc("Leave Allocation",lev)
        comp.cancel()
        frappe.db.commit()


def get_lal(emp, day):
    lal = frappe.db.sql("""select name from `tabLeave Allocation`
                where employee = %s and %s between from_date and to_date and leave_type='Compensatory Off'
         
         
         
            and docstatus = 1""", (emp, day), as_dict=True)
    return lal






def get_lal(emp, day):
    lal = frappe.db.sql("""select name from `tabLeave Allocation`
                where employee = %s and %s between from_date and to_date and leave_type='Compensatory Off'
            and docstatus = 1""", (emp, day), as_dict=True)
    return lal


@frappe.whitelist()
def mark_cl():
    date_time = date.today()
    date1 = frappe.defaults.get_defaults().fiscal_year
    year_start_date = frappe.db.get_value(
        "Fiscal Year", {'name': date1}, ['year_start_date'])
    year_end_date = frappe.db.get_value(
        "Fiscal Year", {'name': date1}, ['year_end_date'])
    d = date_time.strftime("%B %Y")
    employees = frappe.db.sql("""select name from `tabEmployee`
                where status = "Active" and  employment_type != "Contract" and company = "Voltech HR Services Private Limited" and datediff(curdate(),date_of_joining) >= 365  """, as_dict=True)
    for employee in employees:
        emp = frappe.get_doc("Employee", employee)
        cl_ids = get_cl(emp.employee, year_start_date, year_end_date)
        if cl_ids:
            for cl_id in cl_ids:
                cl = frappe.get_doc(
                    "Leave Allocation", cl_id['name'])
                cl.new_leaves_allocated += 1.5
                cl.total_leaves_allocated += 1.5
                if cl.description:
                    cl.description += '<br>' + \
                        'casual Leave for {0} is {1}'.format(
                            date_time, cl.new_leaves_allocated)
                else:
                    cl.description = '<br>' + \
                        'casual Leave for {0} is {1}'.format(
                            date_time, cl.new_leaves_allocated)
                cl.db_update()
                frappe.db.commit
        else:
            cl = frappe.new_doc("Leave Allocation")
            cl.employee = emp.employee
            cl.leave_type = 'casual Leave'
            cl.from_date = year_start_date
            cl.to_date = year_end_date
            cl.new_leaves_allocated = 1.5
            cl.description = 'casual Leave for {0} is {1}'.format(
                date_time, cl.new_leaves_allocated)
            cl.save(ignore_permissions=True)
            cl.submit()
            frappe.db.commit()


def get_cl(emp, year_start_date, year_end_date):
    cl = frappe.db.sql("""select name from `tabLeave Allocation`
                where employee = %s and from_date = %s and to_date = %s and leave_type='casual Leave'
            and docstatus = 1""", (emp, year_start_date, year_end_date), as_dict=True)
    return cl


@frappe.whitelist()
def mark_att():
    days = date.today()
    to_date = (datetime.strptime(str(days), '%Y-%m-%d')).date()
    from_date = add_days(to_date, -3)
    for day in daterange(from_date, to_date):
        att_id = frappe.get_all('Attendance', filters={
                                "docstatus": 0, "attendance_date": day})
        for att in att_id:
            attendance = frappe.get_doc("Attendance", att)
            status = check_record(attendance.employee, day)
            if attendance.status == "On Leave":
                attendance.submit()
                frappe.db.commit()
            elif status == "On Leave" or status == "Half Day":
                attendance.update({
                    "status": status,
                    "total_working_hour": "00:00:00",
                })
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()
            elif status == "On Duty":
                attendance.update({
                    "status": "Present",
                    "total_working_hour": "00:00:00",
                    "onduty_status": status
                })
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()
            else:
                attendance.update({
                    "status": "Absent",
                    "total_working_hour": "00:00:00",
                })
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n)
