# Copyright 2024 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import os

from odoo.addons.shopfloor.services.checkout import Checkout


class CheckoutExt(Checkout):
    _inherit = "base.shopfloor.process"

    def _data_for_packing_info(self, picking):
        res = super()._data_for_packing_info(picking)
        note = picking.note
        if note:
            res += "{}{}".format(os.linesep, note).strip()
        return res
