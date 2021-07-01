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

    def ENDPOINT_TODO(self, todo):
        pass


class ShopfloorDeliveryShipmentValidator(Component):
    """Validators for the Delivery with Shipment Advices endpoints"""

    _inherit = "base.shopfloor.validator"
    _name = "shopfloor.delivery.shipment.validator"
    _usage = "delivery.shipment.validator"

    def ENDPOINT_TODO(self):
        return {
            # TODO
            "TODO": {"required": True, "type": "string"},
        }


class ShopfloorDeliveryShipmentValidatorResponse(Component):
    """Validators for the Delivery with Shipment Advices endpoints responses"""

    _inherit = "base.shopfloor.validator.response"
    _name = "shopfloor.delivery.shipment.validator.response"
    _usage = "delivery.shipment.validator.response"

    _start_state = "TODO"

    def _states(self):
        """List of possible next states

        With the schema of the data send to the client to transition
        to the next state.
        """
        return {
            # TODO
            "STATE1_TODO": self._schema_STATE1_TODO,
            "STATE2_TODO": self._schema_STATE2_TODO,
        }

    @property
    def _schema_STATE1_TODO(self):
        # TODO
        return {}

    @property
    def _schema_STATE2_TODO(self):
        # TODO
        return {}
