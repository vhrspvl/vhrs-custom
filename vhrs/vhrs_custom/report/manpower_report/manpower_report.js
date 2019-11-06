// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Manpower Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_end(),
            "reqd": 1
        },
        // {
        //     "fieldname": "department",
        //     "label": __("Department"),
        //     "fieldtype": "Link",
        //     "options": "Department",
        //     // "default":"% %"
        // },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company")
        }
    ]
}