// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Attendance Sheet VHRS"] = {
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
        "reqd": 1
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
        "reqd": 1
    },
    {
        "fieldname": "business_unit",
        "label": __("Business Unit"),
        "fieldtype": "Link",
        "options": "Business Unit",
        // "default": frappe.defaults.get_user_default("Company"),
        // "reqd": 1
    }
    ],

    "onload": function () {
        return frappe.call({
            method: "erpnext.hr.report.monthly_attendance_sheet.monthly_attendance_sheet.get_attendance_years",
            callback: function (r) {
                var year_filter = frappe.query_report_filters_by_name.year;
                year_filter.df.options = r.message;
                year_filter.df.default = r.message.split("\n")[0];
                year_filter.refresh();
                year_filter.set_input(year_filter.df.default);
            }
        });
    }
}
