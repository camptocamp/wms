# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields

from odoo.addons.stock_release_channel.tests.test_release_channel_partner import (
    ReleaseChannelPartnerCommon,
)


class TestReleaseChannelPartnerDate(ReleaseChannelPartnerCommon):
    def test_release_channel_on_specific_date(self):
        """partner specific date release channel is higher priority than other channels"""
        delivery_date_channel = self.partner_channel.copy(
            {"name": "Specific Date Channel"}
        )
        delivery_date_channel.action_wake_up()
        delivery_date = fields.Datetime.now()
        self.move.picking_id.date_deadline = delivery_date
        pref_rc = self.env["stock.release.channel.partner.date"]
        self.partner.stock_release_channel_by_date_ids = pref_rc.create(
            {
                "partner_id": self.partner.id,
                "release_channel_id": delivery_date_channel.id,
                "date": delivery_date,
            }
        )
        self.moves.picking_id.assign_release_channel()
        self.assertEqual(self.move.picking_id.release_channel_id, delivery_date_channel)
        self.assertEqual(self.move2.picking_id.release_channel_id, self.other_channel)
