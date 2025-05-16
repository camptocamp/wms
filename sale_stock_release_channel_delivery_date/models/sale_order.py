# Copyright 2024 Camptocamp SA
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import api, fields, models
from odoo.tools import ormcache

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("partner_shipping_id", "carrier_id")
    def _compute_expected_date(self):
        res = super()._compute_expected_date()
        for order in self:
            if not order.partner_shipping_id:
                # do not recompute
                continue
            if order.order_line:
                # will be managed at line level
                continue
            if order.state in ["sale", "done"] and order.date_order:
                order_dt = order.date_order
            else:
                order_dt = fields.Datetime.now()
            order.expected_date = order._get_release_channel_expected_date(order_dt)
        return res

    def _get_release_channel_expected_date(self, order_dt):
        self.ensure_one()
        carrier = self.carrier_id
        if not carrier:
            # FIXME: collect from default applied on confirm
            pass
        expected_dt = self._cached_release_channel_expected_date(carrier, order_dt)
        return expected_dt

    @ormcache(
        "self.company_id.id",
        "self.partner_shipping_id.id",
        "self.warehouse_id.id",
        "carrier.id",
        "order_dt",
    )
    def _cached_release_channel_expected_date(self, carrier, order_dt):
        self.ensure_one()
        _logger.debug(f"Computing expected date for {self} starting from {order_dt}")

        channels = self._get_partner_release_channels(carrier)
        if not channels:
            return False
        dates = [
            channel._get_best_delivery_date(self.partner_shipping_id, order_dt)
            for channel in channels
        ]
        return min(dates)

    def _domain_partner_release_channels(self, carrier):
        domain = [
            ("company_id", "=", self.company_id.id),
            ("warehouse_id", "=", self.warehouse_id.id),
        ]
        if carrier:
            domain += [
                "|",
                ("carrier_ids", "=", False),
                ("carrier_ids", "in", carrier),
            ]
        return domain

    @api.model
    def _get_partner_release_channels(self, carrier):
        return (
            self.env["stock.release.channel"]
            .search(self._domain_partner_release_channels(carrier))
            .filtered(
                lambda channel: channel._is_valid_for_partner(self.partner_shipping_id)
            )
        )
