# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()

    data = []
    row = []

    projects = get_project()

    for project in projects:
        if project.customer:
            row = [project.customer]
        else:
            row = [""]

        if project.territory:
            row += [project.territory]
        else:
            row += [""]

        if project.name:
            row += [project.name]
        else:
            row += [""]

        if project.mode_of_interview:
            row += [project.mode_of_interview]
        else:
            row += [""]

        if project.status:
            row += [project.status]
        else:
            row += [""]

        if project.project_status:
            row += [project.project_status]
        else:
            row += [""]

        if project.project_type:
            row += [project.project_type]
        else:
            row += [""]

        if project.expected_start_date:
            row += [project.expected_start_date]
        else:
            row += [""]
        data.append(row)

    return columns, data


def get_columns():
    columns = [
        _("Customer") + ":Link/Customer:150",
        _("Territory") + ":Link/Territory:100",
        _("Projects") + ":Link/Project:150",
        _("MOI") + "::100",
        _("Status") + ":Link/Territory:100",
        _("Project Status") + "::100",
        _("Project Type") + "::100",
        _("Project Date") + ":Date:100",

    ]
    return columns


def get_project():
    projects = frappe.db.sql(
        """select * from tabProject where business_unit = 'BUHR-1'""", as_dict=1)
    return projects
