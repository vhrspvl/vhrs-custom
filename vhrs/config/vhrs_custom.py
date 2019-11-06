from frappe import _


def get_data():
    return [
        {
            "module_name": "VHRS Custom",
            "color": "grey",
            "icon": "fa fa-star",
                    "type": "module",
                    "label": _("VHRS Custom"),
                    "items": [
                        {
                            "type": "doctype",
                            "name": "On Duty Application",
                            "icon": "fa fa-star",
                            "label": _("On Duty Application"),
                            "description": _("VHRS On Duty Application"),
                        }
                    ]
        }
    ]
