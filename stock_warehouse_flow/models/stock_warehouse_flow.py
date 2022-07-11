# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockWarehouseFlow(models.Model):
    _name = "stock.warehouse.flow"
    _description = "Stock Warehouse Routing Flow"

    display_name = fields.Char(store=True)
    from_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        ondelete="restrict",
        string="From operation type",
        required=True,
    )
    carrier_id = fields.Many2one(
        comodel_name="delivery.carrier",
        ondelete="restrict",
        string="Carrier",
        required=True,
    )
    flow_domain = fields.Char(
        string="Source Routing Domain",
        default=[],
        help="Domain based on Stock Moves, to define if the "
        "routing rule is applicable or not.",
    )
    to_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        ondelete="restrict",
        string="To operation type",
        required=True,
    )
    rule_ids = fields.Many2many(
        comodel_name="stock.rule",
        string="Rules",
    )

    @api.depends("carrier_id", "from_picking_type_id", "to_picking_type_id")
    def _compute_display_name(self):
        for flow in self:
            flow.display_name = (
                f"[{flow.carrier_id.display_name}] "
                f"{flow.from_picking_type_id.display_name} => "
                f"{flow.to_picking_type_id.display_name}"
            )
