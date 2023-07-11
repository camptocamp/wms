# Copyright 2023 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class DataDetailAction(Component):
    _inherit = "shopfloor.data.detail.action"

    @property
    def _packaging_detail_parser(self):
        res = super()._packaging_detail_parser
        return res + [
            "is_bundeable",
            "is_prepackaged",
        ]
