// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Report Individual"] = {
    "filters": [
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Select"
        },

    ],


    "onload": function () {
        return frappe.model.get_value('Employee', { 'user_id': frappe.session.user }, 'employee',
            function (data) {
                if (data) {
                    // console.log(employee_filter)
                    // employee_filter.df.default = data['employee']
                    var employee_filter = frappe.query_report_filters_by_name.employee;
                    employee_filter.df.options = data['employee']
                    employee_filter.df.default = data['employee']
                    employee_filter.refresh();
                    employee_filter.set_input(employee_filter.df.default)

                }
            });
    }
}
