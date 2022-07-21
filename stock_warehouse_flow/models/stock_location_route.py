# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, fields, models


class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"

    flow_id = fields.Many2one(
        comodel_name="stock.warehouse.flow",
        ondelete="restrict",
        string="Routing Flow",
    )
    relate_to_flow_ids = fields.One2many(
        comodel_name="stock.warehouse.flow",
        compute="_compute_relate_to_flow_ids",
        string="Replaced by Flows",
    )

    @api.depends("rule_ids.picking_type_id")
    def _compute_relate_to_flow_ids(self):
        for route in self:
            picking_types = route.rule_ids.picking_type_id
            route.relate_to_flow_ids = self.env["stock.warehouse.flow"].search(
                [
                    ("from_picking_type_id", "in", picking_types.ids),
                ]
            )
