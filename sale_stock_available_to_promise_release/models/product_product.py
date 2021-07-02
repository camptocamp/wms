# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_next_replenishment_date(self):
        self.ensure_one()
        picking_type_in = self.env.ref("stock.picking_type_in")
        move_line = self.env["stock.move"].search(
            [
                ("product_id", "=", self.id),
                ("date_expected", ">=", fields.Date.today()),
                ("state", "not in", ["done"]),
                ("picking_type_id", "=", picking_type_in.id),
            ],
            limit=1,
            order="date_expected asc",
        )
        return move_line and move_line.date_expected or False
