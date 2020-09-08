from .common import CommonCase


class TestStockMoveActionAssign(CommonCase):
    @classmethod
    def setUpClassVars(cls, *args, **kwargs):
        super().setUpClassVars(*args, **kwargs)
        cls.wh = cls.env.ref("stock.warehouse0")

    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super().setUpClassBaseData(*args, **kwargs)
        cls.wh.sudo().delivery_steps = "pick_pack_ship"

    def test_assign_after_move_done(self):
        """Ensure we can assign moves after moves in same picking are done"""
        # Normally in odoo, we can't use _action_assign on a single move.
        # It is done on the stock.picking only.
        # In several scenarios, we need to set moves to done individually.
        # However, some code is not planned to behave in this context,
        # for instance, StockPicking._check_entire_pack() is called by
        # StockMove._action_assign() and does not check the state of the
        # move lines, so it modifies "done" move lines.
        package = self.env["stock.quant.package"].create({})
        dest_package1 = self.env["stock.quant.package"].create({})
        dest_package2 = self.env["stock.quant.package"].create({})

        picking = self._create_picking(
            picking_type=self.wh.pick_type_id, lines=[(self.product_a, 50)]
        )
        self._fill_stock_for_moves(picking.move_lines, in_package=package)
        picking.action_assign()

        self.assertEqual(picking.state, "assigned")
        self.assertEqual(picking.package_level_ids.package_id, package)

        # split the move lines in 3, we'll validate 2
        line1 = picking.move_line_ids
        line2 = line1.copy({"product_uom_qty": 8})
        line3 = line1.copy({"product_uom_qty": 12})
        line1.with_context(bypass_reservation_update=True).product_uom_qty = 30

        line2.qty_done = 8
        line2.move_id.split_other_move_lines(line2)
        # we are no longer moving the entire package
        picking.package_level_ids.shallow_unlink()
        line2.result_package_id = dest_package1
        line2.move_id.with_context(_sf_no_backorder=True)._action_done()

        line3.qty_done = 12
        line3.move_id.split_other_move_lines(line3)
        # we are no longer moving the entire package
        picking.package_level_ids.shallow_unlink()
        line3.result_package_id = dest_package2
        line3.move_id.with_context(_sf_no_backorder=True)._action_done()

        # At this point, _action_assign() has automatically been called on the
        # remaining move. At the end of _action_assign(),
        # StockPicking._check_entire_pack() is called, which, by default, look
        # the sum of the move lines qties, and if they match a package, it:
        #
        # * creates a package level
        # * updates all the move lines result package with the package,
        #   including the 'done' lines
        #
        # These checks ensure that we prevent this to happen.
        self.assertEqual(
            picking.move_lines.mapped("state"), ["done", "done", "assigned"]
        )
        self.assertFalse(picking.package_level_ids)
        # we are no longer moving the entire package, must be empty!
        self.assertEqual(line1.result_package_id, self.env["stock.quant.package"])
        self.assertEqual(line2.result_package_id, dest_package1)
        self.assertEqual(line3.result_package_id, dest_package2)
