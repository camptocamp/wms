# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError

from .common import SaleReleaseChannelCase


class TestSaleReleaseChannel(SaleReleaseChannelCase):
    def test_sale_release_channel_auto(self):
        # Without channel: delivery gets automatically the default release channel
        order_auto_channel = self._create_sale_order()
        order_auto_channel.action_confirm()
        picking_out = order_auto_channel.picking_ids
        self.assertFalse(picking_out.release_channel_id)
        self.env["stock.release.channel"].assign_release_channel(picking_out)
        self.assertEqual(picking_out.release_channel_id, self.default_channel)

    def test_sale_release_channel_on_delivery_date(self):
        # Force the channel on order
        order_force_channel = self._create_sale_order(channel=self.test_channel)
        order_force_channel.action_confirm()
        picking_out = order_force_channel.picking_ids
        self.assertFalse(picking_out.release_channel_id)
        self.env["stock.release.channel"].assign_release_channel(picking_out)
        self.assertEqual(picking_out.release_channel_id, self.test_channel)

    def test_inverse_release_channel_id(self):
        test_order = self._create_sale_order(channel=self.test_channel)
        date_ = test_order.commitment_date or test_order.expected_date
        delivery_date = date_ and date_.date()

        with self.assertRaisesRegex(
            UserError, "A customer and shipping address has to be set " "first please."
        ):
            test_order.partner_shipping_id = False
            test_order.release_channel_id = self.default_channel
        test_order.partner_shipping_id = self.customer

        with self.assertRaisesRegex(UserError, "No delivery or expected date defined."):
            test_order.commitment_date = False
            test_order.expected_date = False
            test_order.release_channel_id = self.default_channel
        test_order.commitment_date = date_

        channel_date_model = self.env["stock.release.channel.partner.date"]
        existing_channel_date = channel_date_model.search(
            [
                ("release_channel_id", "=", self.test_channel.id),
                ("date", "=", delivery_date),
            ]
        )
        self.assertTrue(existing_channel_date)
        test_order.release_channel_id = self.default_channel
        deleted_channel_date = channel_date_model.search(
            [
                ("release_channel_id", "=", self.test_channel.id),
                ("date", "=", delivery_date),
            ]
        )
        self.assertFalse(deleted_channel_date)
