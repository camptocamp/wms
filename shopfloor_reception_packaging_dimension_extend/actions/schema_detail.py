# Copyright 2023 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class ShopfloorSchemaDetailAction(Component):
    _inherit = "shopfloor.schema.detail.action"

    def packaging_detail(self):
        schema = super().packaging_detail()
        schema.update(
            {
                "is_bundeable": {
                    "type": "boolean",
                    "nullable": False,
                    "required": False,
                },
                "is_prepackaged": {
                    "type": "boolean",
                    "nullable": False,
                    "required": False,
                },
            }
        )
        return schema
