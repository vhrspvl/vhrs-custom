// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["PM Pending Report"] = {
    "filters": [
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
            "default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
                "Dec"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
        },
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Select",
            "options": "2019\n2020\n2021\n2022",
            "default": "2019",
            "reqd": 1
        },
        {
            "fieldname": "employee_code",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname": "department",
            "label": __("Depratment"),
            "fieldtype": "Link",
            "options": "Department"
        },
        {
            "fieldname": "business_unit",
            "label": __("Business Unit"),
            "fieldtype": "Link",
            "options": "Business Unit"
        },


    ],
    "formatter": function (row, cell, value, columnDef, dataContext, default_formatter) {
        value = default_formatter(row, cell, value, columnDef, dataContext);
        if (columnDef.id == "Self Status") {
            if (dataContext["Self Status"] === "Completed") {
                value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
            }
        }
        if (columnDef.id == "Manager Status") {
            if (dataContext["Manager Status"] === "Completed") {
                value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
            }
        }
        if (columnDef.id == "Reviewer Status") {
            if (dataContext["Reviewer Status"] === "Completed") {
                value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
            }
        }
        return value;
    },
}
