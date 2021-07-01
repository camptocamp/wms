# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

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

    def _response_for_STATE(self, TODO, message=None):
        return self._response(
            next_state="TODO",
            data={
                # TODO
            },
            message=message,
        )

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

    def scan_planned_document(self, barcode):
        """Scan an operation, a package, a product or a lot.

        Transitions:
        """


class ShopfloorDeliveryShipmentValidator(Component):
    """Validators for the Delivery with Shipment Advices endpoints"""

    _inherit = "base.shopfloor.validator"
    _name = "shopfloor.delivery.shipment.validator"
    _usage = "delivery.shipment.validator"

    def scan_dock(self):
        return {
            "barcode": {"required": True, "type": "string"},
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
        # TODO
        return {}

    @property
    def _schema_scan_planned_document(self):
        # TODO
        return {}

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
