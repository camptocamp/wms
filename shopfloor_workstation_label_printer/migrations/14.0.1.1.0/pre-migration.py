# Copyright 2022 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)

try:
    from openupgradelib import openupgrade as ou
except ImportError as exc:
    _logger.debug(exc)
    ou = None


def migrate(cr, version):
    """Move resources from 'shopfloor_workstation_label_printer'."""
    if not version:
        return
    if not ou:
        return
    old_module = "shopfloor_workstation_label_printer"
    new_module = "base_report_to_label_printer"
    ou.update_module_moved_fields(
        cr, "res.users", ["default_label_printer_id"], old_module, new_module
    )
    ou.rename_xmlids(
        cr,
        [
            (f"{old_module}.view_users_form", f"{new_module}.view_users_form"),
            (
                f"{old_module}.view_users_form_simple_modif",
                f"{new_module}.view_users_form_simple_modif",
            ),
        ],
    )
