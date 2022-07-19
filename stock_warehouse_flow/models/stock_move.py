# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _before_release(self):
        super()._before_release()
        for move in self:
            move._find_flow()._apply_on_move(move)

    def _find_flow_domain(self):
        self.ensure_one()
        return [
            ("from_picking_type_id", "=", self.picking_type_id.id),
            ("carrier_id", "in", self.group_id.carrier_ids.ids),
        ]

    def _find_flow(self):
        self.ensure_one()
        return self.env["stock.warehouse.flow"].search(
            self._find_flow_domain(), limit=1
        )
