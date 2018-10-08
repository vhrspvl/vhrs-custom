// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BUHR I - Project Age Report"] = {
    "filters": [
        {
            "fieldname": "start_date",
            "label": __("Start Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "end_date",
            "label": __("End Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
    ],
}