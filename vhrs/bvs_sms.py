from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
import time
import math
import calendar
from dateutil.parser import parse
from frappe.utils.data import today, get_timestamp
from frappe.utils import getdate, cint, add_months, date_diff, add_days, flt, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds, time_diff_in_hours
from datetime import datetime, timedelta
from frappe.core.doctype.sms_settings.sms_settings import send_sms


@frappe.whitelist()
def send_clientsms(candidate_name, status, number, bed):
    rcv = []
    message = """ Voltech HR BGV report status\n Candidate Name : %s \n Overall Status: %s \n Estimated Time Of Closure: %s """ % (
        candidate_name, status, bed)
    rcv.append(number)
    send_sms(rcv, message)
