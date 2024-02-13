# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    release_channel_id = fields.Many2one(
        "stock.release.channel",
        compute="_compute_release_channel_id",
        inverse="_inverse_release_channel_id",
        help=(
            "Specific release channel for the current delivery address based "
            "on expected delivery date."
        ),
    )

    def _compute_release_channel_id(self):
        for rec in self:
            rec.release_channel_id = False
            domain = self._get_release_channel_partner_date_domain()
            if not domain:
                continue
            channel_date = self.env["stock.release.channel.partner.date"].search(domain)
            rec.release_channel_id = channel_date.release_channel_id

    def _inverse_release_channel_id(self):
        channel_date_model = self.env["stock.release.channel.partner.date"]
        for rec in self:
            if not rec.partner_shipping_id:
                raise UserError(
                    _("A customer and shipping address has to be set " "first please.")
                )
            date_ = rec.commitment_date or rec.expected_date
            delivery_date = date_ and date_.date()
            if not delivery_date:
                raise UserError(_("No delivery or expected date defined."))
            if rec.release_channel_id:
                channel_date_model.create(
                    {
                        "release_channel_id": rec.release_channel_id.id,
                        "partner_id": rec.partner_shipping_id.id,
                        "date": delivery_date,
                    }
                )

    def _get_release_channel_partner_date_domain(self):
        self.ensure_one()
        date_ = self.commitment_date or self.expected_date
        delivery_date = date_ and date_.date()
        if not delivery_date:
            return
        return [
            ("partner_id", "=", self.partner_shipping_id.id),
            ("date", "=", delivery_date),
        ]
