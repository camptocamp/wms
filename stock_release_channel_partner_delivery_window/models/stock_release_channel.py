# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import datetime, timedelta

from odoo.addons.stock_release_channel import delivery_date_generator


class StockReleaseChannel(models.Model):

    _inherit = "stock.release.channel"

    respect_partner_delivery_time_windows = fields.Boolean(
        string="Respect Partner Delivery time windows",
        default=False,
        help=(
            "If the delivery has moves linked to SO lines linked to SO that has"
            " a commitment_date, then we never respect the partner time window "
            "(it is not an exclusion selection criteria anymore)"
        ),
    )

    delivery_date_weekday = fields.Integer(
        compute="_compute_delivery_date_weekday",
        store=True,
    )

    # Migration note: shipment_date will be renamed to delivery_date
    @api.depends(
        "shipment_date",
    )
    def _compute_delivery_date_weekday(self):
        for channel in self:
            if channel.shipment_date:
                channel.delivery_date_weekday = channel.shipment_date.weekday()
            else:
                channel.delivery_date_weekday = -1

    @delivery_date_generator(step="customer")
    def _next_delivery_date_partner_delivery_window(self, delivery_date, partner):
        """Get the next valid delivery date respecting customer delivery window.

        The delivery date must be when the customer is open.
        """
        self.ensure_one()
        partner.ensure_one()
        if not self.respect_partner_delivery_time_windows:
            while True:
                delivery_date = yield delivery_date

        if partner.delivery_time_preference == "anytime":
            while True:
                delivery_date = yield delivery_date

        tz = partner.tz
        if partner.delivery_time_preference == "workdays":
            while True:
                delivery_date_tz = self._localize(delivery_date, tz=tz)
                # postpone on Monday if Sat or Sun
                if delivery_date_tz.isoweekday() < 6:  # Mon-Fri
                    delivery_date = yield delivery_date
                    continue
                days = 0
                if delivery_date_tz.isoweekday() == 6:  # Sat
                    days = 1
                elif delivery_date_tz.isoweekday() == 7:  # Sun
                    days = 2
                delivery_date_tz += timedelta(days=days)
                delivery_date = self._naive(delivery_date_tz, reset_time=days)
                delivery_date = yield delivery_date

        while True:
            delivery_date_tz = self._localize(delivery_date, tz=tz)
            weekday = delivery_date_tz.weekday()
            for inc in range(8):
                windows = partner.delivery_time_window_ids.filtered(
                    lambda w: str(weekday + inc)
                    in w.time_window_weekday_ids.mapped("name")
                    and (inc or w.get_time_window_end_time() >= delivery_date_tz.time())
                )
                if windows:
                    w = windows[0]
                    break
            else:
                # There is no time window, we consider any date valid
                while True:
                    delivery_date = yield delivery_date
            delivery_date_tz = datetime.combine(
                (delivery_date_tz + timedelta(days=inc)).date(),
                max(w.get_time_window_start_time(), delivery_date_tz.time())
                if not inc
                else w.get_time_window_start_time(),
                tzinfo=delivery_date_tz.tzinfo,
            )
            delivery_date = self._naive(delivery_date_tz)
            delivery_date = yield delivery_date
