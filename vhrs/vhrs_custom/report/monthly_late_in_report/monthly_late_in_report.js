// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Late-in Report"] = {
    "filters": [{
        "fieldname": "month",
        "label": __("Month"),
        "fieldtype": "Select",
        "options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
        "default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
            "Dec"
        ][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
    },
    {
        "fieldname": "year",
        "label": __("Year"),
        "fieldtype": "Select",
        "reqd": 0,
        "options": ["2018", "2019", "2020"]
    },
    {
        "fieldname": "employee",
        "label": __("Employee"),
        "fieldtype": "Link",
        "options": "Employee"
    },
    {
        "fieldname": "company",
        "label": __("Company"),
        "fieldtype": "Link",
        "options": "Company",
        "default": frappe.defaults.get_user_default("Company"),
        "reqd": 0
    },
    {
        "fieldname": "business_unit",
        "label": __("Business Unit"),
        "fieldtype": "Link",
        "options": "Business Unit",
        // "default": frappe.defaults.get_user_default("Company"),
        // "reqd": 1
    }
    ]

}
