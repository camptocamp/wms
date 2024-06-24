# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    preferred_release_channel_ids = fields.One2many(
        related="partner_shipping_id.preferred_release_channel_ids",
        readonly=False,
    )
    preferred_release_channel_id = fields.Many2one(
        "stock.release.channel",
        compute="_compute_preferred_release_channel_id",
        help=(
            "Technical field returning the preferred release channel "
            "for the current delivery address based on expected delivery date."
        ),
    )

    @api.depends("partner_shipping_id.preferred_release_channel_ids.date")
    def _compute_preferred_release_channel_id(self):
        for rec in self:
            rec.preferred_release_channel_id = False
            date_ = rec.commitment_date or rec.expected_date
            delivery_date = date_ and date_.date()
            if not delivery_date:
                continue
            pref_rc = self.env["stock.preferred.release.channel"].search(
                [
                    ("partner_id", "=", rec.partner_shipping_id.id),
                    ("date", "=", delivery_date),
                ]
            )
            rec.preferred_release_channel_id = pref_rc.release_channel_id
