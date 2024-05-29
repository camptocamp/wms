# Copyright 2023 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from odoo import fields

from odoo.addons.shipment_advice.tests.common import Common
from odoo.addons.shopfloor_reception.tests.common import CommonCase


class ShopfloorReceptionShipmentAdvice(CommonCase, Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.menu.sudo().picking_type_ids = [(4, cls.picking_type_in.id)]
        cls.picking = cls.move_product_in1.picking_id
        cls.pickings = cls.picking
        cls.shipment_in = cls.shipment_advice_in
        cls.shipment_in.arrival_date = fields.Datetime.now()
        cls.shipment_in.action_confirm()
        cls.shipment_out = cls.shipment_advice_out

    def setUp(self):
        super().setUp()
        self.service = self.get_service(
            "reception",
            menu=self.menu,
            profile=self.profile,
            current_shipment_advice=self.shipment_in,
        )

    def _get_today_picking(self):
        return self.env["stock.picking"].search(
            self.service._domain_stock_picking(today_only=True),
            order=self.service._order_stock_picking(),
        )

    def _data_for_shipment(self, picking=None, shipment=None):
        data = {}
        if picking:
            data = self._data_for_select_move(picking)
        if shipment:
            data.pop("picking", None)
            data["shipment"] = self.data_detail.shipment_advice_detail(shipment)
        return data

    def test_scan_dock_ok(self):
        """Check scanning a dock returns the list of available shipments."""
        dock = self.dock
        dock.barcode = "dock-barcode"
        self.shipment_in.dock_id = self.dock
        response = self.service.dispatch(
            "scan_document", params={"barcode": dock.barcode}
        )
        data = {
            "dock": self.data.dock(dock),
            "shipments": [self.data.shipment_advice(self.shipment_in)],
        }
        self.assert_response(
            response,
            next_state="manual_selection_shipment",
            data=data,
        )

    def test_scan_shipment_error_outgoing(self):
        """Check scanning an outgoing shipment is refused."""
        response = self.service.dispatch(
            "scan_document", params={"barcode": self.shipment_out.name}
        )
        self.assert_response(
            response,
            next_state="select_document",
            data={
                "pickings": self.service._data_for_stock_pickings(
                    self._get_today_picking(), with_lines=False
                ),
            },
            message=self.service.msg_store.shipment_incoming_type_only(),
        )

    def test_scan_shipment_error_empty(self):
        """Check scanning a shipment with nothing to unload."""
        shipment = self.shipment_in
        response = self.service.dispatch(
            "scan_document", params={"barcode": shipment.name}
        )
        self.assert_response(
            response,
            next_state="select_document",
            data={
                "pickings": self.service._data_for_stock_pickings(
                    self._get_today_picking(), with_lines=False
                ),
            },
            message=self.service.msg_store.shipment_nothing_to_unload(shipment),
        )

    def test_scan_shipment_advice_with_one_picking(self):
        shipment = self.shipment_advice_in
        self._plan_records_in_shipment(shipment, self.picking)
        response = self.service.dispatch(
            "scan_document", params={"barcode": shipment.name}
        )
        self.assert_response(
            response,
            next_state="select_move",
            data=self._data_for_shipment(
                shipment.planned_picking_ids, shipment=shipment
            ),
        )

    def test_scan_shipment_advice_with_two_picking(self):
        shipment = self.shipment_advice_in
        self._plan_records_in_shipment(shipment, self.picking)
        picking_2 = self.picking.copy()
        self._plan_records_in_shipment(shipment, picking_2)
        response = self.service.dispatch(
            "scan_document", params={"barcode": shipment.name}
        )
        self.assert_response(
            response,
            next_state="select_move",
            data=self._data_for_shipment(
                shipment.planned_picking_ids, shipment=shipment
            ),
        )

    def test_scan_line_barcode_not_found(self):
        shipment = self.shipment_advice_in
        response = self.service.dispatch(
            "scan_line",
            params={"picking_id": None, "shipment_id": shipment.id, "barcode": "NOPE"},
        )
        self.assert_response(
            response,
            next_state="select_move",
            data=self._data_for_shipment(shipment=shipment),
            message={"message_type": "error", "body": "Barcode not found"},
        )

    def test_scan_line_barcode_product(self):
        shipment = self.shipment_advice_in
        self.picking.action_confirm()
        self._plan_records_in_shipment(shipment, self.picking)
        product = self.picking.move_lines.product_id
        product.barcode = "BARCODE-01"
        selected_move_line = fields.first(
            self.picking.move_line_ids.filtered(lambda l: l.product_id == product)
        )
        response = self.service.dispatch(
            "scan_line",
            params={
                "picking_id": None,
                "shipment_id": shipment.id,
                "barcode": "BARCODE-01",
            },
        )
        self.assert_response(
            response,
            next_state="set_quantity",
            data={
                "picking": self.data.picking(self.picking),
                "selected_move_line": self.data.move_lines(selected_move_line),
                "confirmation_required": None,
            },
        )

    def test_scan_line_barcode_packaging(self):
        shipment = self.shipment_advice_in
        self.picking.action_confirm()
        self._plan_records_in_shipment(shipment, self.picking)
        product = self.picking.move_lines.product_id
        packaging = self.product_a_packaging = (
            self.env["product.packaging"]
            .sudo()
            .create(
                {
                    "name": "Box",
                    "product_id": product.id,
                    "barcode": "ProductTestBox",
                    "qty": 3.0,
                }
            )
        )
        product.barcode = "BARCODE-01"
        selected_move_line = fields.first(
            self.picking.move_line_ids.filtered(lambda l: l.product_id == product)
        )
        response = self.service.dispatch(
            "scan_line",
            params={
                "picking_id": None,
                "shipment_id": shipment.id,
                "barcode": packaging.barcode,
            },
        )
        self.assert_response(
            response,
            next_state="set_quantity",
            data={
                "picking": self.data.picking(self.picking),
                "selected_move_line": self.data.move_lines(selected_move_line),
                "confirmation_required": None,
            },
        )

    def test_auto_post_line(self):
        picking = self._create_picking(
            scheduled_date=fields.Datetime.today() + timedelta(days=1)
        )
        move_line_a = picking.move_line_ids.filtered(
            lambda l: l.product_id == self.product_a
        )
        move_line_a.write(
            {
                "shipment_advice_id": self.shipment_advice_in,
                "qty_done": 10.0,
            }
        )
        move_line_b = picking.move_line_ids.filtered(
            lambda l: l.product_id == self.product_b
        )
        shipment_advice_in_2 = self.env["shipment.advice"].create(
            {"shipment_type": "incoming"}
        )
        move_line_b.write(
            {
                "shipment_advice_id": shipment_advice_in_2,
                "qty_done": 10.0,
            }
        )
        self.assertEqual(move_line_a.shipment_advice_id.state, "confirmed")
        self.assertEqual(move_line_b.shipment_advice_id.state, "draft")
        self.assertEqual(picking.state, "assigned")
        # Auto posting line a, shipment for line a should be done
        self.service._auto_post_line(move_line_a)
        self.assertEqual(move_line_a.shipment_advice_id.state, "done")
        self.assertEqual(move_line_b.shipment_advice_id.state, "draft")
        self.assertEqual(picking.state, "assigned")
        # Auto posting line b, shipment for line b should be done
        # When likes are posted, picking should be done too
        self.service._auto_post_line(move_line_b)
        self.assertEqual(move_line_a.shipment_advice_id.state, "done")
        self.assertEqual(move_line_b.shipment_advice_id.state, "done")
        self.assertEqual(picking.state, "done")

    def test_handle_backorder(self):
        picking = self._create_picking(
            scheduled_date=fields.Datetime.today() + timedelta(days=1)
        )
        picking_due_today = self._create_picking(scheduled_date=fields.Datetime.today())
        selected_move_line = picking.move_line_ids.filtered(
            lambda l: l.product_id == self.product_a
        )
        selected_move_line.write(
            {
                "shipment_advice_id": self.shipment_advice_in,
                "qty_done": 10.0,
            }
        )
        unselected_move_line = picking.move_line_ids.filtered(
            lambda l: l.product_id == self.product_b
        )
        shipment_advice_in_2 = self.env["shipment.advice"].create(
            {"shipment_type": "incoming"}
        )
        unselected_move_line.write(
            {
                "shipment_advice_id": shipment_advice_in_2,
            }
        )
        self.assertEqual(unselected_move_line.shipment_advice_id.state, "draft")
        response = self.service.dispatch(
            "done_action", params={"picking_id": picking.id}
        )
        # Checking if we get msg about creating backorder
        self.assert_response(
            response,
            next_state="confirm_done",
            data={"picking": self._data_for_picking_with_moves(picking)},
            message={
                "message_type": "warning",
                "body": (
                    "Not all lines have been processed with full quantity. "
                    "Do you confirm partial operation?"
                ),
            },
        )
        self.assertEqual(selected_move_line.shipment_advice_id.state, "confirmed")
        self.assertEqual(unselected_move_line.shipment_advice_id.state, "draft")
        # On dispatch, we trigger done_action, which sets selected_move_line
        # shipment_advice to "done" state if shipment is fully done
        response = self.service.dispatch(
            "done_action", params={"picking_id": picking.id, "confirmation": True}
        )
        self.assertEqual(selected_move_line.shipment_advice_id.state, "done")
        self.assertEqual(picking.state, "done")
        # Running backorder flow
        backorder = picking.backorder_ids
        self.assertEqual(backorder.move_line_ids.product_id, self.product_b)
        self.assertEqual(unselected_move_line.shipment_advice_id.state, "draft")
        self.assert_response(
            response,
            next_state="select_document",
            data={"pickings": self._data_for_pickings(picking_due_today)},
            message={
                "message_type": "success",
                "body": f"Transfer {picking.name} done",
            },
        )
