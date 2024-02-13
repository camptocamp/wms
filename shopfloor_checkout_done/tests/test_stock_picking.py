from odoo.addons.shopfloor.tests.test_checkout_base import CheckoutCommonCase


class TestStockPicking(CheckoutCommonCase):
    def test_put_in_pack(self):
        picking = self._create_picking(
            lines=[(self.product_a, 10), (self.product_b, 20)]
        )
        self._fill_stock_for_moves(picking.move_lines)
        picking.action_assign()

        # Test that the move lines are marked as 'shopfloor_checkout_done'
        # when putting them in a pack in the backend.
        picking._put_in_pack(picking.move_line_ids)
        self.assertTrue(
            all(line.shopfloor_checkout_done for line in picking.move_line_ids)
        )

        # Check that we return those lines to the frontend.
        res = self.service.dispatch(
            "summary",
            params={
                "picking_id": picking.id,
            },
        )
        returned_lines = res["data"]["summary"]["picking"]["move_lines"]
        expected_line_ids = [line["id"] for line in returned_lines]
        self.assertEqual(expected_line_ids, picking.move_line_ids.ids)
