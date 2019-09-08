frappe.listview_settings['Performance Management'] = {
    add_fields: ["employee_name", "name", "pending"],
    get_indicator: function (doc) {
        if (doc.status == 0) {
            return [__(doc.status), frappe.utils.guess_colour(doc.status),
            "status,=," + doc.status];
        }
        if (doc.status == 1) {
            return [__(doc.status), frappe.utils.guess_colour(doc.status),
            "status,=," + doc.status];
        }
    },
    refresh: function (me) {
        me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
        me.page.sidebar.find(".list-link[data-view='Tree']").addClass("hide");
        me.page.sidebar.find(".assigned-to-me a").addClass("hide");
        // if (frappe.user.has_role("Employee") && frappe.user.has_role("Operations Manager")) {
        //     frappe.route_options = {
        //         "operations_manager": ["=", frappe.session.user],
        //         "pending": ["=", "Manager Pending"],
        //     };
        // } else if (frappe.user.has_role("Employee") && frappe.user.has_role("Unit Head")) {
        //     frappe.route_options = {
        //         "unit_head": ["=", frappe.session.user],
        //         "pending": ["=", "Reviewer Pending"]
        //     };
        // } else if (frappe.user.has_role("Employee") && !frappe.user.has_role("Operations Manager") && !frappe.user.has_role("Unit Head")) {
        //     frappe.route_options = {
        //         "user_id": ["=", frappe.session.user],
        //         "pending": ["=", "Self Pending"]
        //     };
        // }
        // if (frappe.route_options = { "user_id": ["=", frappe.session.iser] }) {
        //     frappe.route_options = {
        //         "pending": ["=", "Self Pending"],
        //     };
        // }
    }

};