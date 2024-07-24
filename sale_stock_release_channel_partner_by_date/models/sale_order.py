# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    release_channel_id = fields.Many2one(
        comodel_name="stock.release.channel",
        compute="_compute_release_channel_id",
        store=True,
        readonly=False,
        index=True,
        help=(
            "Specific release channel for the current delivery address based "
            "on expected delivery date."
        ),
    )
    release_channel_partner_date_id = fields.Many2one(
        comodel_name="stock.release.channel.partner.date",
        compute="_compute_release_channel_partner_date_id",
    )

    @api.depends("commitment_date")
    def _compute_release_channel_id(self):
        for rec in self:
            rec.release_channel_id = False
            domain = rec._get_release_channel_partner_date_domain()
            if not domain:
                continue
            channel_date = rec.release_channel_partner_date_id
            if channel_date:
                rec.release_channel_id = channel_date.release_channel_id

    @api.depends(
        "state",
        "partner_shipping_id",
        "commitment_date",
        "expected_date",
        "release_channel_id",
    )
    def _compute_release_channel_partner_date_id(self):
        for rec in self:
            channel_partner_date = rec._get_release_channel_partner_date()
            rec.release_channel_partner_date_id = channel_partner_date

    def _get_release_channel_partner_date(self):
        self.ensure_one()
        model = self.env["stock.release.channel.partner.date"]
        domain = self._get_release_channel_partner_date_domain()
        return domain and model.search(domain, limit=1) or model

    def _get_release_channel_partner_date_domain(self):
        self.ensure_one()
        delivery_date = self._get_delivery_date()
        if not delivery_date:
            return
        return [
            ("partner_id", "=", self.partner_shipping_id.id),
            ("date", "=", delivery_date),
        ]

    def action_confirm(self):
        # Create specific channel entry on order confirmation
        res = super().action_confirm()
        for rec in self:
            rec._create_release_channel_partner_date()
        return res

    def _action_cancel(self):
        # Store specific channel entries before cancelling them as
        # expected_date is unset on cancel orders
        channel_entries = {o.id: o.release_channel_partner_date_id for o in self}
        # Remove specific channel entry when canceling order
        res = super()._action_cancel()
        for rec in self:
            rec._unlink_release_channel_partner_date(
                channel_date=channel_entries[rec.id]
            )
        return res

    def _create_release_channel_partner_date(self):
        self.ensure_one()
        model = self.env["stock.release.channel.partner.date"]
        if self.state != "sale" or not self.release_channel_id:
            return model
        channel_dates = (
            self.release_channel_id.release_channel_partner_date_ids.filtered_domain(
                self._get_release_channel_partner_date_domain()
            )
        )
        if not channel_dates:
            values = self._prepare_release_channel_partner_date_values()
            return model.create(values)
        return model

    def _prepare_release_channel_partner_date_values(self):
        self.ensure_one()
        delivery_date = self._get_delivery_date()
        assert delivery_date
        return {
            "release_channel_id": self.release_channel_id.id,
            "partner_id": self.partner_shipping_id.id,
            "date": delivery_date,
        }

    def _unlink_release_channel_partner_date(self, channel_date):
        self.ensure_one()
        if self.state != "cancel":
            return False
        # Check if specific channel entry is used by another order
        if channel_date:
            other_orders = self.search(
                [
                    ("id", "!=", self.id),
                    ("state", "in", ("draft", "sent", "sale")),
                    ("delivery_status", "!=", "full"),
                    ("release_channel_id", "=", channel_date.release_channel_id.id),
                    ("partner_shipping_id", "=", channel_date.partner_id.id),
                ]
            ).filtered(lambda o: o._get_delivery_date() == channel_date.date)
            if not other_orders:
                channel_date.unlink()
        return False

    def _get_delivery_date(self):
        self.ensure_one()
        date = self.commitment_date or self.expected_date
        tz = self.warehouse_id.partner_id.tz or self.env.company.partner_id.tz or "UTC"
        return (
            date
            and fields.Datetime.context_timestamp(
                self.with_context(tz=tz),
                date,
            ).date()
        )
