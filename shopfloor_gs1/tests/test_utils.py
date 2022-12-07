# Copyright 2022 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime

from odoo.tests.common import BaseCase

from ..utils import GS1Barcode


class TestUtils(BaseCase):
    def test_parse1(self):
        code = "(01)09506000117843(11)141231(10)1234AB"
        res = GS1Barcode.parse(code)
        self.assertEqual(len(res), 3, res)
        item = [x for x in res if x.type == "product"][0]
        self.assertEqual(item.ai, "01")
        self.assertEqual(item.code, code)
        self.assertEqual(item.value, "09506000117843")
        self.assertEqual(item.raw_value, "09506000117843")
        item = [x for x in res if x.type == "production_date"][0]
        self.assertEqual(item.ai, "11")
        self.assertEqual(item.code, code)
        self.assertEqual(item.value, datetime.date(2014, 12, 31))
        self.assertEqual(item.raw_value, "141231")
        item = [x for x in res if x.type == "lot"][0]
        self.assertEqual(item.ai, "10")
        self.assertEqual(item.code, code)
        self.assertEqual(item.value, "1234AB")
        self.assertEqual(item.raw_value, "1234AB")

    def test_parse2(self):
        code = "(01)09506000117843(11)141231(10)1234AB"
        res = GS1Barcode.parse(code, ai_whitelist=("01",))
        self.assertEqual(len(res), 1, res)
        item = [x for x in res if x.type == "product"][0]
        self.assertEqual(item.ai, "01")
        self.assertEqual(item.code, code)
        self.assertEqual(item.value, "09506000117843")
        self.assertEqual(item.raw_value, "09506000117843")
