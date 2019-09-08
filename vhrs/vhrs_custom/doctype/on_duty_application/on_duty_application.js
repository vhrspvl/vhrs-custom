// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt
cur_frm.add_fetch('employee', 'company', 'company');
frappe.ui.form.on('On Duty Application', {
    onload: function (frm) {
        if (!frm.doc.posting_date) {
            frm.set_value("posting_date", frappe.datetime.get_today());
        }

        frm.set_query("approver", function () {
            return {
                query: "erpnext.hr.doctype.leave_application.leave_application.get_approvers",
                filters: {
                    employee: frm.doc.employee
                }
            };
        });

        frm.set_query("employee", erpnext.queries.employee);

    },
    half_day: function (frm) {
        if (frm.doc.half_day == 1) {
            frm.set_df_property('half_day_date', 'reqd', true);
        }
        else {
            frm.set_df_property('half_day_date', 'reqd', false);
        }
    },

    refresh: function (frm) {
        if (frm.is_new()) {
            frm.set_value("status", "Open");
            frm.trigger("calculate_total_days");
        }
    },
    // half_day: function (frm) {
    //     if (frm.doc.half_day == 1) {
    //         frm.set_df_property('half_day_date', 'reqd', true);
    //     }
    //     else {
    //         frm.set_df_property('half_day_date', 'reqd', false);
    //     }
    // },
    half_day: function (frm) {
        if (frm.doc.from_date == frm.doc.to_date) {
            frm.set_value("half_day_date", frm.doc.from_date);
        }
        else {
            frm.trigger("half_day_datepicker");
        }
        frm.trigger("calculate_total_days");
    },

    from_date: function (frm) {
        frm.trigger("half_day_datepicker");
        frm.trigger("calculate_total_days");
    },

    to_date: function (frm) {
        frm.trigger("half_day_datepicker");
        frm.trigger("calculate_total_days");
    },

    half_day_date(frm) {
        frm.trigger("calculate_total_days");
    },

    half_day_datepicker: function (frm) {
        frm.set_value('half_day_date', '');
        var half_day_datepicker = frm.fields_dict.half_day_date.datepicker;
        half_day_datepicker.update({
            minDate: frappe.datetime.str_to_obj(frm.doc.from_date),
            maxDate: frappe.datetime.str_to_obj(frm.doc.to_date)
        })
    },

    calculate_total_days: function (frm) {
        if (frm.doc.from_date && frm.doc.to_date && frm.doc.employee && frm.doc.leave_type) {
            // server call is done to include holidays in leave days calculations
            return frappe.call({
                method: 'vhrs.vhrs_custom.doctype.on_duty_application.on_duty_application.get_number_of_leave_days',
                args: {
                    "employee": frm.doc.employee,
                    "leave_type": frm.doc.leave_type,
                    "from_date": frm.doc.from_date,
                    "to_date": frm.doc.to_date,
                    "half_day": frm.doc.half_day,
                    "half_day_date": frm.doc.half_day_date,
                },
                callback: function (r) {
                    if (r && r.message) {
                        frm.set_value('total_leave_days', r.message);

                    }
                }
            });
        }
    },

});
