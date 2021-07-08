# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields

from odoo.addons.shopfloor.tests import common


class DeliveryShipmentCommonCase(common.CommonCase):
    @classmethod
    def setUpClassVars(cls, *args, **kwargs):
        super().setUpClassVars(*args, **kwargs)
        cls.menu = cls.env.ref(
            "shopfloor_delivery_shipment.shopfloor_menu_delivery_shipment"
        )
        cls.profile = cls.env.ref("shopfloor_base.profile_demo_1")
        # Change menu picking type to ease test (avoid to configure pick+pack+ship)
        cls.wh = cls.menu.picking_type_ids.warehouse_id
        cls.picking_type = cls.menu.sudo().picking_type_ids = cls.wh.out_type_id
        cls.picking_type.sudo().show_entire_packs = True
        cls.dock = cls.env.ref("shipment_advice.stock_dock_demo")
        cls.dock.sudo().barcode = "DOCK"

    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super().setUpClassBaseData(*args, **kwargs)
        # Create 3 deliveries
        cls.pickings = cls.env["stock.picking"]
        for i in range(1, 4):
            picking = cls._create_picking(
                cls.picking_type,
                lines=[
                    # we'll put A and B in a single package
                    (cls.product_a, 10),
                    (cls.product_b, 10),
                    # C as raw product
                    (cls.product_c, 10),
                ],
            )
            cls.pickings |= picking
            setattr(cls, f"picking{i}", picking)
            pack_moves = picking.move_lines[:2]
            raw_move = picking.move_lines[2]
            cls._fill_stock_for_moves(pack_moves, in_package=True)
            cls._fill_stock_for_moves(raw_move, in_lot=True)
            picking.action_assign()
        # Create a shipment advice
        cls.shipment = cls._create_shipment()

    def setUp(self):
        super().setUp()
        with self.work_on_services(menu=self.menu, profile=self.profile) as work:
            self.service = work.component(usage="delivery_shipment")

    @classmethod
    def _create_shipment(cls):
        return cls.env["shipment.advice"].create(
            {
                "shipment_type": "outgoing",
                "dock_id": cls.dock.id,
                "arrival_date": fields.Datetime.now(),
            }
        )

    @classmethod
    def _plan_records_in_shipment(cls, shipment_advice, records):
        wiz_model = cls.env["wizard.plan.shipment"].with_context(
            active_model=records._name, active_ids=records.ids,
        )
        wiz = wiz_model.create({"shipment_advice_id": shipment_advice.id})
        wiz.action_plan()
        return wiz

    def _data_for_shipment_advice(self, shipment_advice):
        return self.service.data.shipment_advice(shipment_advice)

    def _data_for_stock_picking(self, picking):
        return self.service._data_for_stock_picking(picking)

    def assert_response_scan_dock(self, response, message=None):
        self.assert_response(response, next_state="scan_dock", message=message)

    def assert_response_scan_document(
        self, response, shipment_advice, picking=None, message=None
    ):
        data = {
            "shipment_advice": self._data_for_shipment_advice(shipment_advice),
        }
        if picking:
            data["picking"] = self.service.data.picking(picking)
            data["content"] = self.service._data_for_content_to_load(
                shipment_advice, picking
            )
        self.assert_response(
            response, next_state="scan_document", data=data, message=message,
        )
