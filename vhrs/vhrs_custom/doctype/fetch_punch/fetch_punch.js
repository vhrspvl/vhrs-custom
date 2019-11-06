// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fetch Punch', {
    refresh: function (frm) {
        frm.disable_save()
    },
    fetch: function (frm) {
        frappe.call({
            method: "vhrs.utils.fetch_from_ui",
            args: {
                "from_date": frm.doc.from_date,
                "to_date": frm.doc.to_date,
                "fetch_type": "punch"
            },
            freeze: true,
            freeze_message: "Fetching",
            callback: function (r) {
                if (r) {
                    frappe.msgprint(__("Punch Fetched"));
                }
            }
        })

    }
});
