// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Management Manager', {
    refresh: function (frm) {

    },
    date_of_rating: function (frm) {
        var monthNames = [
            "Jan", "Feb", "Mar",
            "Apr", "May", "Jun", "Jul",
            "Aug", "Sep", "Oct",
            "Nov", "Dec"
        ];
        var date = new Date(frm.doc.date_of_rating);
        var day = date.getDate();
        var monthIndex = date.getMonth();
        var year = date.getFullYear();
        var moe = monthNames[monthIndex] + year;
        frm.set_value("month", moe);
    },
    onload: function (frm) {
        cur_frm.fields_dict['kra_rating_manager'].grid.wrapper.find('.grid-remove-rows').hide();
        cur_frm.fields_dict['kra_rating_manager'].grid.wrapper.find('.grid-add-row').hide();
    }
});
