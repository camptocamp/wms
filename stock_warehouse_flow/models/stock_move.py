# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _before_release(self):
        # Apply the flow when releasing the move
        # TODO: to move in a glue module depending
        # on 'stock_available_to_promise_release'
        super()._before_release()
        for move in self:
            flow = self.env["stock.warehouse.flow"]._search_for_move(move)
            flow._apply_on_move(move)
