# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    has_lq_products = fields.Boolean(compute="_compute_has_lq_products")

    def _compute_has_lq_products(self):
        for record in self:
            record.has_lq_products = any(
                record.mapped("quant_ids.product_id.is_lq_product")
            )
