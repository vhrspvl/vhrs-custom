frappe.listview_settings['Performance Management Manager'] = {
    // onload:function(frm){
    //     frm.trigger("refresh")
    // },
    refresh: function (me) {
        me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
        me.page.sidebar.find(".list-link[data-view='Tree']").addClass("hide");
        me.page.sidebar.find(".assigned-to-me a").addClass("hide");
        if (!frappe.user.has_role("System Manager")) {
            if (!frappe.route_options) {
                frappe.route_options = {
                    "operations_manager": ["=", frappe.session.user]
                };
            }
        }
    }

};