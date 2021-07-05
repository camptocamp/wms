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
