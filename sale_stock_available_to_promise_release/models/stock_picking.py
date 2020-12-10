# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    sale_date_expected = fields.Date(
        string="Delivery Date", related="group_id.date_expected", store=True
    )

    def _get_shipping_policy(self):
        # Override the method to get the shipping policy from the related order
        self.ensure_one()
        return self.sale_id.picking_policy or super()._get_shipping_policy()
