# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields

from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component


class DeliveryShipment(Component):
    """Methods for the Delivery with Shipment Advices process

    Deliver the goods by processing the PACK and raw products by delivery order
    into a shipment advice.

    Multiple operators could be processing a same delivery order.

    You will find a sequence diagram describing states and endpoints
    relationships [here](../docs/delivery_shipment_diag_seq.png).
    Keep [the sequence diagram](../docs/delivery_shipment_diag_seq.plantuml)
    up-to-date if you change endpoints.

    Three cases:

    * Manager assign shipment advice to loading dock, plan its content and start them
    * Manager assign shipment advice to loading dock without content planning and start them
    * Operators create shipment advice on the fly (option “Allow shipment advice creation”
      in the scenario)

    Expected:

    * Existing packages are moved to customer location
    * Products are moved to customer location as raw products
    * Bin packed products are placed in new shipping package and shipped to customer
    * A shipment advice is marked as done
    """

    _inherit = "base.shopfloor.process"
    _name = "shopfloor.delivery.shipment"
    _usage = "delivery_shipment"
    _description = __doc__

    def _response_for_scan_dock(self, message=None):
        return self._response(next_state="scan_dock", message=message)

    def _response_for_scan_document(self, shipment_advice, picking=None, message=None):
        data = {
            "shipment_advice": self.data.shipment_advice(shipment_advice),
        }
        if picking:
            data.update(picking=self._data_for_stock_picking(picking))
        return self._response(next_state="scan_document", data=data, message=message,)

    def _data_for_stock_picking(self, picking):
        data = self.data.picking(picking)
        # TODO: send package levels and lines w/o packages (with lot if any)
        #       all sorted and grouped by source location
        data.update(
            content={
                # "move_lines": self._data_for_move_lines(
                #     line_picker(picking), with_packaging=done
                # )
            }
        )
        return data

    def _data_for_move_lines(self, lines, **kw):
        return self.data.move_lines(lines, **kw)

    def _find_shipment_advice_from_dock(self, dock):
        return self.env["shipment.advice"].search(
            [("dock_id", "=", dock.id), ("state", "in", ["in_progress"])],
            limit=1,
            order="arrival_date",
        )

    def _create_shipment_advice_from_dock(self, dock):
        shipment_advice = self.env["shipment.advice"].create(
            {
                "dock_id": dock.id,
                "arrival_date": fields.Datetime.to_string(fields.Datetime.now()),
            }
        )
        shipment_advice.action_confirm()
        shipment_advice.action_in_progress()
        return shipment_advice

    def scan_dock(self, barcode):
        """Scan a loading dock.

        Called at the beginning of the workflow to select the shipment advice
        (corresponding to the scanned loading dock) to work on.

        If no shipment advice in progress related to the scanned loading dock
        is found, a new one is created if the menu as the option
        "Allow to create shipment advice" enabled.

        Transitions:
        * scan_document: a shipment advice has been found or created (with or
          without planned moves)
        * scan_dock: no shipment advice found
        """
        search = self._actions_for("search")
        dock = search.dock_from_scan(barcode)
        if dock:
            shipment_advice = self._find_shipment_advice_from_dock(dock)
            if not shipment_advice:
                if not self.work.menu.allow_shipment_advice_create:
                    return self._response_for_scan_dock(
                        message=self.msg_store.no_shipment_in_progress(dock)
                    )
                shipment_advice = self._create_shipment_advice_from_dock(dock)
            return self._response_for_scan_document(shipment_advice)
        return self._response_for_scan_dock(message=self.msg_store.barcode_not_found())

    def scan_document(self, shipment_advice_id, barcode, picking_id=None):
        """Scan an operation, a package, a product or a lot.

        If an operation is scanned, reload the screen with the related
        planned content of this operation for this shipment advice.

        If a package, a product or a lot is scanned, it will be loaded in the
        current shipment advice and the screen will be reloaded with the related
        operation listing its planned content.

        Transitions:
        * scan_document: once a good is loaded, or a operation has been
          scanned, or in case of error
        * scan_dock: error (shipment not found...)
        """
        shipment_advice = (
            self.env["shipment.advice"].browse(shipment_advice_id).exists()
        )
        if not shipment_advice:
            return self._response_for_scan_dock(
                message=self.msg_store.record_not_found()
            )
        picking = None
        if picking_id:
            picking = self.env["stock.picking"].browse(picking_id).exists()
            if not picking:
                return self._response_for_scan_document(
                    shipment_advice, message=self.msg_store.stock_picking_not_found()
                )
        # TODO
        # if scanned_picking:
        #   return self._scan_picking(shipment_advice, scanned_picking)
        # if scanned_package:
        #   return self._scan_package(shipment_advice, scanned_package)
        # if scanned_lot:
        #   return self._scan_product(shipment_advice, scanned_lot)
        # if scanned_product:
        #   return self._scan_product(shipment_advice, scanned_product)
        return self._response_for_scan_document(
            shipment_advice, picking, message=self.msg_store.barcode_not_found()
        )

    def _scan_package(self, shipment_advice, package):
        """Load the package in the shipment advice.

        Find the package level (of the planned shipment advice in
        priority if any) corresponding to the scanned package and load it.
        If no package level is found an error will be returned.
        """
        # TODO
        package_level = package
        message = None
        return self._response_for_scan_document(
            shipment_advice, package_level.picking_id, message=message
        )

    def _scan_lot(self, shipment_advice, lot):
        """Load the lot in the shipment advice.

        Find the first move line (of the planned shipment advice in
        priority if any) corresponding to the scanned lot and load it.
        If no move line is found an error will be returned.
        """
        # TODO
        move_line = lot
        message = None
        return self._response_for_scan_document(
            shipment_advice, move_line.picking_id, message=message
        )

    def _scan_product(self, shipment_advice, product):
        """Load the product in the shipment advice.

        Find the first move line (of the planned shipment advice in
        priority if any) corresponding to the scanned product and load it.
        If no move line is found an error will be returned.
        """
        # TODO
        move_line = product
        message = None
        return self._response_for_scan_document(
            shipment_advice, move_line.picking_id, message=message
        )

    def loading_list(self, shipment_advice_id):
        # TODO
        pass

    def validate_shipment(self, shipment_advice_id, confirm=False):
        # TODO
        pass


class ShopfloorDeliveryShipmentValidator(Component):
    """Validators for the Delivery with Shipment Advices endpoints"""

    _inherit = "base.shopfloor.validator"
    _name = "shopfloor.delivery.shipment.validator"
    _usage = "delivery.shipment.validator"

    def scan_dock(self):
        return {
            "barcode": {"required": True, "type": "string"},
        }

    def scan_document(self):
        return {
            "shipment_advice_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            },
            "barcode": {"required": True, "type": "string"},
            "picking_id": {
                "coerce": to_int,
                "required": False,
                "nullable": True,
                "type": "integer",
            },
        }

    def loading_list(self):
        return {
            "shipment_advice_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            },
        }

    def validate_shipment(self):
        return {
            "shipment_advice_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            },
            "confirm": {
                "coerce": to_bool,
                "required": False,
                "nullable": True,
                "type": "boolean",
            },
        }


class ShopfloorDeliveryShipmentValidatorResponse(Component):
    """Validators for the Delivery with Shipment Advices endpoints responses"""

    _inherit = "base.shopfloor.validator.response"
    _name = "shopfloor.delivery.shipment.validator.response"
    _usage = "delivery.shipment.validator.response"

    _start_state = "scan_dock"

    def _states(self):
        """List of possible next states

        With the schema of the data send to the client to transition
        to the next state.
        """
        return {
            "scan_dock": self._schema_scan_dock,
            "scan_document": self._schema_scan_document,
            "loading_list": self._schema_loading_list,
            "validate_shipment": self._schema_validate_shipment,
        }

    @property
    def _schema_scan_dock(self):
        return {}

    @property
    def _schema_scan_document(self):
        shipment_schema = self.schemas.shipment_advice()
        picking_schema = self.schemas.picking_detail()
        return {
            "shipment_advice": {
                "type": "dict",
                "nullable": False,
                "schema": shipment_schema,
            },
            "picking": {"type": "dict", "nullable": True, "schema": picking_schema},
        }

    @property
    def _schema_loading_list(self):
        shipment_schema = self.schemas.shipment_advice()
        # TODO
        return {
            "shipment_advice": {
                "type": "dict",
                "nullable": False,
                "schema": shipment_schema,
            },
        }

    @property
    def _schema_validate_shipment(self):
        shipment_schema = self.schemas.shipment_advice()
        # TODO
        return {
            "shipment_advice": {
                "type": "dict",
                "nullable": False,
                "schema": shipment_schema,
            },
        }

    def scan_dock(self):
        return self._response_schema(next_states={"scan_document", "scan_dock"})

    def scan_document(self):
        return self._response_schema(next_states={"scan_document", "scan_dock"})

    def loading_list(self):
        return self._response_schema(next_states={"loading_list", "scan_dock"})

    def validate_shipment(self):
        return self._response_schema(next_states={"validate_shipment", "scan_dock"})
