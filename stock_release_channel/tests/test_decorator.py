# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


from odoo import fields
from odoo.tests.common import TransactionCase

from odoo.addons.stock_release_channel import decorators

from .models import generator_test  # noqa


class TestStockReleaseChannelDecorator(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.main_partner")
        cls.channel = cls.env.ref("stock_release_channel.stock_release_channel_default")
        cls.dt = fields.Datetime.now()

    def test_generator_correct(self):
        """Test generator on channel object"""
        funcs = decorators.delivery_date_generators.get("preparation")
        self.assertTrue(len(funcs) > 0)
        for func in funcs:
            func(self.channel, self.dt, self.partner)

    def test_generator_wrong(self):
        """Test generator on wrong object"""
        funcs = decorators.delivery_date_generators.get("preparation")
        self.assertTrue(len(funcs) > 0)
        for func in funcs:
            with self.assertRaisesRegex(Exception, "delivery_date_generator"):
                func(self.partner, self.dt, self.partner)
