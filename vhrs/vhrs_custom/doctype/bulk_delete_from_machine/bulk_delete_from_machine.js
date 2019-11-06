// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk delete from machine', {
    bulk_delete: function (frm) {
        frappe.call({
            method: "vhrs.custom.delete_bulk",
            freeze: true,
            callback: function (r) {
                console.log(r.message)
                // if (r.message === 'OK') {
                //     frappe.msgprint(__("Deleted from Machine"))
                // }
            }
        })
    }
});
