// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Day Attendance"] = {
	"filters": [
		{
			"fieldname": "date",
			"label": __("Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname": "hrsic",
			"label": __("HRSIC"),
			"fieldtype": "Link",
			"options": "HRSIC"
		},
		
],
	"formatter": function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);
		if (dataContext["Remarks"] === "Late") {
			value = "<span style='color:red!important;font-weight:bold'>" + value + "</span>";
		}
		return value;
	}
}