# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.base_rest.components.service import to_int
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

    def _response_for_scan_planned_document(
        self, shipment_advice, picking=None, message=None
    ):
        data = {
            "shipment_advice": None,  # TODO
        }
        if picking:
            data.update(picking=self._data_for_stock_picking(picking))
        return self._response(
            next_state="scan_planned_document", data=data, message=message,
        )

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

    def scan_dock(self, barcode):
        """Scan a loading dock.

        Called at the beginning of the workflow to select the shipment advice
        (corresponding to the scanned loading dock) to work on.

        If no shipment advice in progress related to the scanned loading dock
        is found, a new one is created if the menu as the option
        "Allow to create shipment advice" enabled.

        Transitions:
        * scan_planned_document: a shipment advice with planned moves has been found
        * scan_unplanned_document: a shipment advice without planned moves has been
          found or created
        * scan_dock: no shipment advice found
        """
        # TODO

    def scan_planned_document(self, shipment_advice_id, barcode, picking_id=None):
        """Scan an operation, a package, a product or a lot.

        If an operation is scanned, reload the screen with the related
        planned content of this operation for this shipment advice.

        If a package, a product or a lot is scanned, it will be loaded in the
        current shipment advice and the screen will be reloaded with the related
        operation listing its planned content.

        Transitions:
        * scan_planned_document: once a good is loaded, or a operation has been
          scanned, or in case of error
        * scan_dock: error (shipment not found...)
        """
        # TODO


class ShopfloorDeliveryShipmentValidator(Component):
    """Validators for the Delivery with Shipment Advices endpoints"""

    _inherit = "base.shopfloor.validator"
    _name = "shopfloor.delivery.shipment.validator"
    _usage = "delivery.shipment.validator"

    def scan_dock(self):
        return {
            "barcode": {"required": True, "type": "string"},
        }

    def scan_planned_document(self):
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

    def scan_unplanned_document(self):
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
            # TODO
            "scan_dock": self._schema_scan_dock,
            "scan_planned_document": self._schema_scan_planned_document,
            "scan_unplanned_document": self._schema_scan_unplanned_document,
        }

    @property
    def _schema_scan_dock(self):
        return {}

    @property
    def _schema_scan_planned_document(self):
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
    def _schema_scan_unplanned_document(self):
        # TODO
        return {}

    def scan_dock(self):
        return self._response_schema(
            next_states={
                "scan_planned_document",
                "scan_unplanned_document",
                "scan_dock",
            }
        )

    def scan_planned_document(self):
        return self._response_schema(next_states={"scan_planned_document", "scan_dock"})
