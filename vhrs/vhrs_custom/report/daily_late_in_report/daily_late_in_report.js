// Copyright (c) 2016, Starboxes India and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Late-in Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        // {
        //     "fieldname": "employee",
        //     "label": __("Employee"),
        //     "fieldtype": "Link",
        //     "options": "Employee"
        // },


        // {
        // 	"fieldname": "user",
        // 	"label": __("Employee"),
        // 	"fieldtype": "Data",
        // 	"default": frappe.session.user,
        // 	"hidden": 1
        // },
    ],

}