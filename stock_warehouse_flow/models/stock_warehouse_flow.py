# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

# TODO
# Chaque WH a plusieurs routes (std)
#   - Chaque WH a plusieurs flux (nouveau smart button)
#   - Un flux est lié qu'à un seul WH
#   - Chaque flux pointe vers une route (flow.delivery_route_id)
#   - Ajouter une option "delivery_steps", qui générera automatiquement
#     la delivery route + les rules associées

from odoo import api, fields, models


class StockWarehouseFlow(models.Model):
    _name = "stock.warehouse.flow"
    _description = "Stock Warehouse Routing Flow"

    # TODO add warehouse_id
    name = fields.Char()
    from_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        ondelete="restrict",
        string="From operation type",
        required=True,
        # TODO: default to the out_type_id of the WH
    )
    from_location_src_id = fields.Many2one(
        comodel_name="stock.location",
        compute="_compute_from_location_src_id",
    )
    from_location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        compute="_compute_from_location_dest_id",
    )
    # FIXME: restrict selection of to picking type on from picking type dest loc
    to_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        ondelete="restrict",
        string="To operation type",
        required=True,
    )
    carrier_ids = fields.Many2many(
        comodel_name="delivery.carrier",
        string="Carriers",
    )
    # FIXME to integrate
    flow_domain = fields.Char(
        string="Source Routing Domain",
        default=[],
        help="Domain based on Stock Moves, to define if the "
        "routing flow is applicable or not.",
    )
    rule_ids = fields.Many2many(
        comodel_name="stock.rule",
        string="Rules",
        domain="[('location_src_id', 'child_of', from_location_src_id)]",
    )

    @api.depends("from_picking_type_id.default_location_src_id")
    def _compute_from_location_src_id(self):
        for record in self:
            location = record.from_picking_type_id.default_location_src_id
            if not location:
                __, location = self.env["stock.warehouse"]._get_partner_locations()
            record.from_location_src_id = location

    @api.depends("from_picking_type_id.default_location_dest_id")
    def _compute_from_location_dest_id(self):
        for record in self:
            location = record.from_picking_type_id.default_location_dest_id
            if not location:
                location, __ = self.env["stock.warehouse"]._get_partner_locations()
            record.from_location_dest_id = location

    def _apply_on_move(self, move):
        """Apply the flow configuration on the move."""
        move.picking_id = False
        move.picking_type_id = self.to_picking_type_id
        move.location_id = self.to_picking_type_id.default_location_src_id
        move._assign_picking()
