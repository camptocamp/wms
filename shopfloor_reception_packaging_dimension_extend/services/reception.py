# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.osv import expression

from odoo.addons.component.core import Component


class Reception(Component):
    _inherit = "shopfloor.reception"

    def set_packaging_dimension(
        self,
        picking_id,
        selected_line_id,
        packaging_id,
        height=None,
        length=None,
        width=None,
        weight=None,
        qty=None,
        barcode=None,
        cancel=False,
        is_bundeable=None,
        is_prepackaged=None,
    ):
        self._store_dimension_to_update(["is_bundeable", "is_prepackaged"], locals())
        return super().set_packaging_dimension(
            picking_id,
            selected_line_id,
            packaging_id,
            height,
            length,
            width,
            weight,
            qty,
            barcode,
            cancel,
        )

    def _check_dimension_to_update(self):
        res = super()._check_dimension_to_update()
        if not res:
            dimension_to_check = ["is_bundeable", "is_prepackaged"]
            return any(
                [self.dimension_to_update.get(dim, False) for dim in dimension_to_check]
            )
        return res

    def _update_packaging_dimension(self, packaging):
        super()._update_packaging_dimension(packaging)
        dimension_to_update = ["is_bundeable", "is_prepackaged"]
        for dimension in dimension_to_update:
            value = self.dimension_to_update.get(dimension, None)
            if value is not None:
                packaging[dimension] = value

    def _get_domain_packaging_needs_dimension(self):
        domain = super()._get_domain_packaging_needs_dimension()
        return expression.OR(
            [
                domain,
                # Searching for all fields set to NULL but it does not work
                [
                    ("is_bundeable", "!=", False),
                    ("is_bundeable", "!=", True),
                ],
                [
                    ("is_prepackaged", "!=", False),
                    ("is_prepackaged", "!=", True),
                ],
            ]
        )


class ShopfloorReceptionValidator(Component):
    _inherit = "shopfloor.reception.validator"

    def set_packaging_dimension(self):
        res = super().set_packaging_dimension()
        res.update(
            {
                "is_bundeable": {
                    "required": False,
                    "type": "boolean",
                    "nullable": True,
                },
                "is_prepackaged": {
                    "required": False,
                    "type": "boolean",
                    "nullable": True,
                },
            }
        )
        return res
