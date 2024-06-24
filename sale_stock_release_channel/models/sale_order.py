# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    preferred_release_channel_ids = fields.One2many(
        related="partner_shipping_id.preferred_release_channel_ids",
        readonly=False,
    )
