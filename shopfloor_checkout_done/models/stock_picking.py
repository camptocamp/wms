# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class Picking(models.Model):
    _inherit = "stock.picking"

    def _put_in_pack(self, move_line_ids, create_package_level=True):
        """
        Marks the corresponding move lines as 'shopfloor_checkout_done'
        when the package is created in the backend.

        """
        new_package = super()._put_in_pack(move_line_ids, create_package_level)
        lines = self.move_line_ids.filtered(
            lambda p: p.result_package_id == new_package
        )
        lines.write({"shopfloor_checkout_done": True})
        return new_package
