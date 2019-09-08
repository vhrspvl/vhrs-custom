// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Management', {
    editable: function (frm) {
        if (frm.doc.pending == "First Reviewer") {
            if (frappe.session.user == frm.doc.operations_manager) {
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.self_rating.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.description.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.weightage.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.reviewer.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.kra_rating.df.read_only = 1;
            } else {
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.self_rating.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.description.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.weightage.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.reviewer.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.kra_rating.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.manager.df.read_only = 1;
            }
        }
        if (frm.doc.pending == "Second Reviewer") {
            if (frappe.session.user == frm.doc.unit_head) {
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.self_rating.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.description.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.weightage.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.manager.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.kra_rating.df.read_only = 1;
            } else {
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.self_rating.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.description.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.weightage.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.reviewer.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.kra_rating.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.manager.df.read_only = 1;
            }
        }
        if (frm.doc.pending == "Second Reviewer Completed") {
            cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.self_rating.df.read_only = 1;
            cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.description.df.read_only = 1;
            cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.weightage.df.read_only = 1;
            cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.reviewer.df.read_only = 1;
            cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.kra_rating.df.read_only = 1;
            cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.manager.df.read_only = 1;
        }

        if (frm.doc.pending == "Self") {
            if (frappe.session.user == frm.doc.user_id) {

                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.reviewer.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.kra_rating.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.manager.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.description.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.weightage.df.read_only = 1;
            } else {
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.self_rating.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.description.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.weightage.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.reviewer.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.kra_rating.df.read_only = 1;
                cur_frm.get_field("kra_rating_reviewer").grid.grid_rows[0].columns.manager.df.read_only = 1;
            }
        }
    },
    refresh: function (frm) {
        frm.trigger("editable")
    },
    onload: function (frm) {
        frm.trigger("editable")
        c = frm.doc.kra_rating_reviewer
        cl = c.length
        if (frm.doc.pending == "Self" && cl == 1) {
            frm.clear_table("kra_rating_reviewer");
            child = []
            child_len = child.length
            if (frm.doc.employee_code && child_len == 0) {
                if (frm.doc.employee_code) {
                    frappe.call({
                        "method": "frappe.client.get",
                        args: {
                            "doctype": "Employee",
                            "name": frm.doc.employee_code
                        },
                        callback: function (r) {
                            if (r.message) {
                                var child = r.message.kra_rating_details
                                var len = child.length
                                if (len != 0) {
                                    for (var i = 0; i < len; i++) {
                                        var kra_type = ""
                                        // if (child[i].description == "Conversion of Closure to SO") {
                                        //     kra_type = "Closure"
                                        // }
                                        // if (child[i].description == "Cracking A+ Accounts") {
                                        //     kra_type = "Lead"
                                        // }
                                        // if (child[i].description == "Client Shortlisted Vs Closure") {
                                        //     kra_type = "CandidatePSL"
                                        // }
                                        // if (child[i].description == "Candidate Collection Against Target") {
                                        //     kra_type = "CollectionDnD"
                                        // }
                                        // if (child[i].description == "No. of Opportunities in Hand") {
                                        //     kra_type = "Opportunity"
                                        // }
                                        // if (kra_type) {
                                        //     frappe.call({
                                        //         "method": "vhrs.vhrs_custom.doctype.performance_management.performance_management.auto_generate_kra",
                                        //         args: {
                                        //             "kra_type": kra_type,
                                        //             "pm_date": frm.doc.date_of_rating,
                                        //             "executive": "anita.k@voltechgroup.com"
                                        //         },
                                        //         callback: function (r) {
                                        //             // console.log(r.message)
                                        //         }
                                        //     })
                                        // }
                                        var row = frappe.model.add_child(frm.doc, "KRA Rating Reviewer", "kra_rating_reviewer");
                                        row.description = child[i].description
                                        row.weightage = child[i].weightage
                                    }
                                    frm.refresh_field("kra_rating_reviewer")
                                }
                            }
                        }
                    })
                }
            }
            frm.trigger("editable")
        }
    },

    employee_code: function (frm) {
        frappe.call({
            "method": "frappe.client.get",
            args: {
                "doctype": "Employee",
                "name": frm.doc.employee_code
            },
            callback: function (r) {
                if (r.message) {
                    frm.set_value("employee_name", r.message.employee_name)
                    frm.set_value("short_code", r.message.short_code)
                    frm.set_value("department", r.message.department)
                    frm.set_value("designation", r.message.designation)
                    frm.set_value("business_unit", r.message.business_unit)
                    frm.set_value("branch", r.message.branch)
                    frm.set_value("work_level", r.message.work_level)
                    frm.set_value("date_of_joining", r.message.date_of_joining)
                    frm.set_value("date_of_rating", frappe.datetime.nowdate())
                    frm.set_value("operations_manager", r.message.operations_manager)
                    frm.set_value("unit_head", r.message.second_reviewer)
                }
            }
        })
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
    calculate_avg: function (frm) {
        pr_rating = 0.0
        $.each(frm.doc.kra_rating_reviewer || [], function (i, v) {
            if (v.reviewer) {
                var total = ((v.reviewer * v.weightage) / 100)
            }
            if (v.kra_rating) {
                pr_rating += v.kra_rating

            }
        })
        total_pr = pr_rating.toFixed(2)
        frm.set_value("pr_rating", pr_rating)
        frm.set_df_property('pr_rating', 'read_only', 1);
    },
    calculate_avg_self: function (frm) {
        pr_rating = 0.0
        $.each(frm.doc.kra_rating_reviewer || [], function (i, v) {
            if (v.self) {
                var total = ((v.self * v.weightage) / 100)
            }
            if (v.kra_rating) {
                pr_rating += v.kra_rating

            }
        })
        total_pr = pr_rating.toFixed(2)
        frm.set_value("pr_rating", pr_rating)
        frm.set_df_property('pr_rating', 'read_only', 1);
    },
    calculate_avg_manager: function (frm) {
        pr_rating = 0.0
        $.each(frm.doc.kra_rating_reviewer || [], function (i, v) {
            if (v.manager) {
                var total = ((v.manager * v.weightage) / 100)
            }
            if (v.kra_rating) {
                pr_rating += v.kra_rating

            }
        })
        total_pr = pr_rating.toFixed(2)
        frm.set_value("pr_rating", pr_rating)
        frm.set_df_property('pr_rating', 'read_only', 1);
    },
    // onload: function (frm) {
    //     if (frm.doc.pending != "Self") {
    //         cur_frm.fields_dict['kra_rating_reviewer'].grid.wrapper.find('.grid-remove-rows').hide();
    //         cur_frm.fields_dict['kra_rating_reviewer'].grid.wrapper.find('.grid-add-row').hide();
    //     }
    // },
    pr_rating: function (frm) {
        if (frm.doc.pr_rating < 4) {
            frm.set_value("grade", "E")
        } else if ((frm.doc.pr_rating >= 4) && (frm.doc.pr_rating < 5)) {
            frm.set_value("grade", "D")
        } else if ((frm.doc.pr_rating >= 5) && (frm.doc.pr_rating < 6)) {
            frm.set_value("grade", "C")
        } else if ((frm.doc.pr_rating >= 6) && (frm.doc.pr_rating < 7.5)) {
            frm.set_value("grade", "B")
        } else if ((frm.doc.pr_rating >= 7.5) && (frm.doc.pr_rating < 8)) {
            frm.set_value("grade", "B+")
        } else if ((frm.doc.pr_rating >= 8) && (frm.doc.pr_rating < 9.5)) {
            frm.set_value("grade", "A")
        } else if (frm.doc.pr_rating >= 9.5) {
            frm.set_value("grade", "A+")
        }
    },
    validate: function (frm) {
        var goals = ""
        var child1 = frm.doc.kra_rating_reviewer;
        var len1 = child1.length;
        var total1 = 0;
        if (child1) {
            for (var i = 0; i < len1; i++) {
                total1 += child1[i].weightage;
            }
            if (total1 != 100) {
                validated = false
                frappe.throw(__("In Performance Measurement Weightage Must be equal to 100"))
                goals = "Not Ok"
            } else if (total1 == 100) {
                goals = "Ok"
            }
        }
        if (goals == "Ok") {
            frappe.call({
                "method": "frappe.client.get",
                args: {
                    "doctype": "Employee",
                    "name": frm.doc.employee_code
                },
                callback: function (r) {
                    if (r.message.user_id == frappe.session.user) {
                        if (frm.doc.pending == "Self") {
                            if (frm.doc.operations_manager != "-") {
                                frm.set_value("pending", "First Reviewer")
                                setTimeout(function () { window.history.back(); }, 500);
                            } else {
                                frm.set_value("pending", "Second Reviewer")
                                $.each(frm.doc.kra_rating_reviewer, function (i, d) {
                                    d.manager = "NA"
                                    refresh_field("kra_rating_reviewer")
                                })
                                setTimeout(function () { window.history.back(); }, 500);
                            }
                        }
                    }
                    if ((r.message.operations_manager == frm.doc.operations_manager) && (r.message.operations_manager == frappe.session.user)) {
                        if (frm.doc.pending == "First Reviewer") {
                            frm.set_value("pending", "Second Reviewer")
                            setTimeout(function () { window.history.back(); }, 500);
                        }
                    }
                    if (frm.doc.unit_head == frappe.session.user) {
                        if (frm.doc.pending == "Second Reviewer") {
                            frm.set_value("pending", "Second Reviewer Completed")
                        }
                    }
                }
            })

        }

    },
    on_submit: function (frm) {
        if (frm.doc.pending == "SR Completed") {
            setTimeout(function () { window.history.back(); }, 500);
        }
    }

});

frappe.ui.form.on("KRA Rating Reviewer", {
    description: function (frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        var des = child.description
        frappe.call({
            "method": "frappe.client.get",
            args: {
                "doctype": "Goals",
                "name": child.description
            },
            callback: function (r) {
                w = r.message.wightage
                frappe.model.set_value(child.doctype, child.name, "weightage", w);
            }
        })
        var child1 = frm.doc.kra_rating_reviewer
        var len = child1.length
        if (len > 1 && child.description) {
            for (var i = 0; i < len - 1; i++) {
                if (child1[i].description == des) {
                    frappe.msgprint("Already You Choosed the Same")
                }
            }
        }
    },
    reviewer: function (frm, cdt, cdn) {
        if (frm.doc.unit_head == frappe.session.user) {
            var child = locals[cdt][cdn];
            // if (child.reviewer) {
            var total = ((child.reviewer * child.weightage) / 100)
            frappe.model.set_value(child.doctype, child.name, "kra_rating", total);
            // }
            frm.trigger("calculate_avg")
        }
        if (child.reviewer > 10) {
            frappe.model.set_value(child.doctype, child.name, "reviewer", " ");
            frappe.msgprint("Rating Must be less than or Equal to 10")
        }
    },
    self_rating: function (frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        if (frm.doc.user_id == frappe.session.user) {
            // if (child.self_rating) {
            var total = ((child.self_rating * child.weightage) / 100)
            frappe.model.set_value(child.doctype, child.name, "kra_rating", total);
            // }
            frm.trigger("calculate_avg_self")
        }
        if (child.self_rating > 10) {
            frappe.model.set_value(child.doctype, child.name, "self_rating", " ");
            frappe.msgprint("Rating Must be less than or Equal to 10")
        }
    },
    manager: function (frm, cdt, cdn) {
        if (frm.doc.operations_manager == frappe.session.user) {
            var child = locals[cdt][cdn];
            // if (child.manager) {
            var total = ((child.manager * child.weightage) / 100)
            frappe.model.set_value(child.doctype, child.name, "kra_rating", total);
            // }
            frm.trigger("calculate_avg_self")
        }
        if (child.manager > 10) {
            frappe.model.set_value(child.doctype, child.name, "manager", " ");
            frappe.msgprint("Rating Must be less than or Equal to 10")
        }
    },
})