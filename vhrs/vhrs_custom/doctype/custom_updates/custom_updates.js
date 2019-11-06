// Copyright (c) 2017, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Custom Updates', {
	refresh: function (frm) {

	}
});

frappe.ui.form.on("Sales Order", {
	customer: function (frm) {
		frm.set_value("candidates", "");
		if (frm.doc.customer) {
			frappe.call({
				method: "vhrs.custom.get_candidates",
				args: {
					"customer": frm.doc.customer
				},
				callback: function (r) {
					if (r.message) {
						$.each(r.message, function (i, d) {
							var row = frappe.model.add_child(frm.doc, "Sales Order Candidate", "candidates");
							row.candidate_name = d.name;
							row.passport_no = d.passport_no;
						});
					}
					refresh_field("candidates");
					// frm.trigger("calculate_total_amount");
				}
			});
		}
	},
});






