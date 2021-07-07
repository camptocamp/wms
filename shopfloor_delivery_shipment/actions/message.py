# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _

from odoo.addons.component.core import Component


class MessageAction(Component):
    _inherit = "shopfloor.message.action"

    def no_shipment_in_progress(self, dock):
        return {
            "message_type": "error",
            "body": _("No shipment in progress found for dock {}.").format(dock.name),
        }

    def picking_not_planned_in_shipment(self, picking, shipment_advice):
        return {
            "message_type": "error",
            "body": _("Transfer %s has not been planned in the shipment {}.").format(
                picking.name, shipment_advice.name,
            ),
        }

    def carrier_not_allowed_by_shipment(self, picking):
        return {
            "message_type": "error",
            "body": _(
                "Delivery method {} not permitted for this shipment advice."
            ).format(picking.carrier_id.name,),
        }
