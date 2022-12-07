# Copyright 2022 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

from odoo.tests.common import SavepointCase


class TestNomenclature(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.nom = cls.env["barcode.nomenclature"].create({"name": "test"})

    def test_parse1(self):
        with mock.patch.object(type(self.nom), "parse_barcode_gs1") as mocked:
            self.nom.parse_barcode("foo")
            mocked.assert_not_called()

    def test_parse2(self):
        self.nom.is_gs1_nomenclature = True
        with mock.patch.object(type(self.nom), "parse_barcode_gs1") as mocked:
            self.nom.parse_barcode("foo")
            mocked.assert_called_with("foo", ai_whitelist=None)
