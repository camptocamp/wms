# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.shopfloor_reception.tests.common import CommonCase


class TestSetPackDimensionExtend(CommonCase):
    @classmethod
    def setUpClassBaseData(cls):
        super().setUpClassBaseData()
        # Activate the option to use the module
        cls.menu.sudo().set_packaging_dimension = True
        cls.picking = cls._create_picking(
            lines=[(cls.product_a, 10), (cls.product_b, 10), (cls.product_c, 10)]
        )
        # Picking has 3 products
        # Product A with one packaging
        # Product B with no packaging
        cls.product_b.packaging_ids = [(5, 0, 0)]
        # Product C with 2 packaging
        cls.product_c_packaging_2 = (
            cls.env["product.packaging"]
            .sudo()
            .create(
                {
                    "name": "Big Box",
                    "product_id": cls.product_c.id,
                    "barcode": "ProductCBigBox",
                    "qty": 6,
                }
            )
        )

        cls.line_with_packaging = cls.picking.move_line_ids[0]
        cls.line_without_packaging = cls.picking.move_line_ids[1]

    def _assert_response_set_dimension(
        self, response, picking, line, packaging, message=None
    ):
        data = {
            "picking": self.data.picking(picking),
            "selected_move_line": self.data.move_line(line),
            "packaging": self.data_detail.packaging_detail(packaging),
        }
        self.assert_response(
            response,
            next_state="set_packaging_dimension",
            data=data,
            message=message,
        )

    # def test_scan_product_ask_for_dimension(self):
    #     self.product_a.tracking = "none"
    #     # self._add_package(self.picking)
    #     self.assertTrue(self.product_a.packaging_ids)
    #     response = self.service.dispatch(
    #         "scan_line",
    #         params={
    #             "picking_id": self.picking.id,
    #             "barcode": self.product_a.barcode,
    #         },
    #     )
    #     self.data.picking(self.picking)
    #     selected_move_line = self.picking.move_line_ids.filtered(
    #         lambda l: l.product_id == self.product_a
    #     )
    #     self._assert_response_set_dimension(
    #         response, self.picking, selected_move_line, self.product_a_packaging
    #     )

    def test_set_packaging_dimension(self):
        self.assertEqual(self.product_a_packaging.is_bundeable, False)
        selected_move_line = self.picking.move_line_ids.filtered(
            lambda l: l.product_id == self.product_a
        )
        self.service.dispatch(
            "set_packaging_dimension",
            params={
                "picking_id": self.picking.id,
                "selected_line_id": selected_move_line.id,
                "packaging_id": self.product_a_packaging.id,
                "cancel": False,
                "is_bundeable": True,
            },
        )
        self.assertEqual(self.product_a_packaging.is_bundeable, True)
        self.product_a_packaging.is_bundeable = False
        #
        self.assertEqual(self.product_a_packaging.is_prepackaged, False)
        selected_move_line = self.picking.move_line_ids.filtered(
            lambda l: l.product_id == self.product_a
        )
        self.service.dispatch(
            "set_packaging_dimension",
            params={
                "picking_id": self.picking.id,
                "selected_line_id": selected_move_line.id,
                "packaging_id": self.product_a_packaging.id,
                "cancel": False,
                "is_prepackaged": True,
            },
        )
        self.assertEqual(self.product_a_packaging.is_bundeable, False)
        self.assertEqual(self.product_a_packaging.is_prepackaged, True)
