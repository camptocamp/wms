# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import Form

from odoo.addons.stock_release_channel.tests.common import ReleaseChannelCase


class SaleReleaseChannelCase(ReleaseChannelCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref("account.group_delivery_invoice_address")
        cls.customer = cls.env.ref("base.res_partner_1")
        cls.default_channel.sequence = 1
        cls.test_channel = cls.default_channel.copy({"name": "Test", "sequence": 10})
        cls.test_channel.action_wake_up()

    @classmethod
    def _create_sale_order(cls, channel=False, date=False):
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.customer
        with sale_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom_qty = 1
        # Set a preferred channel after lines to get an expected_date
        if channel:
            with sale_form.preferred_release_channel_ids.new() as pref_rc_form:
                # pref_rc_form.partner_id = sale_form.partner_id
                pref_rc_form.release_channel_id = channel
                pref_rc_form.date = date or sale_form.expected_date
        return sale_form.save()
