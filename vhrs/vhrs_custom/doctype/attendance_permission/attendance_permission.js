// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Permission', {
    // onload: function (frm) {
    //     if (!frm.doc.posting_date) {
    //         frm.set_value("posting_date", frappe.datetime.get_today());
    //     }

    //     frm.set_query("approver", function () {
    //         return {
    //             query: "erpnext.hr.doctype.leave_application.leave_application.get_approvers",
    //             filters: {
    //                 employee: frm.doc.employee
    //             }
    //         };
    //     });

    //     frm.set_query("employee", erpnext.queries.employee);

    // },
    // refresh: function (frm) {
    //     if (frm.is_new()) {
    //         frm.set_value("status", "Open");
    //     }
    // },
});
