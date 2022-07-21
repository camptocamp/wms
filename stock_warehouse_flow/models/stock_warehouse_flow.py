# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

# TODO
#   - Ajouter une option "delivery_steps", qui générera automatiquement
#     la delivery route + les rules associées

import logging

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

logger = logging.getLogger(__name__)


class StockWarehouseFlow(models.Model):
    _name = "stock.warehouse.flow"
    _description = "Stock Warehouse Routing Flow"

    name = fields.Char()
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        ondelete="restrict",
        string="Warehouse",
    )
    from_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        ondelete="restrict",
        string="From operation type",
        required=True,
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
        string="With carriers",
    )
    move_domain = fields.Char(
        string="Source Routing Domain",
        default=[],
        help="Domain based on Stock Moves, to define if the "
        "routing flow is applicable or not.",
    )
    delivery_route_id = fields.Many2one(
        "stock.location.route",
        string="Delivery Route",
        ondelete="restrict",
        readonly=True,
    )
    # TODO rules should be a related field through 'delivery_route_id' and
    # they should be limited to the flow config (current domain)
    rule_ids = fields.One2many(
        related="delivery_route_id.rule_ids",
        string="Rules",
    )
    impacted_route_ids = fields.One2many(
        comodel_name="stock.location.route",
        compute="_compute_impacted_route_ids",
        string="Impacted Routes",
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

    def _compute_impacted_route_ids(self):
        for flow in self:
            rules = self.env["stock.rule"].search(
                [
                    ("picking_type_id", "=", flow.from_picking_type_id.id),
                    ("route_id.flow_id", "=", False),
                ]
            )
            flow.impacted_route_ids = rules.route_id

    @api.onchange("warehouse_id")
    def onchange_warehouse_id(self):
        self.from_picking_type_id = self.warehouse_id.out_type_id

    def action_view_all_routes(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_routes_form")
        action["domain"] = [("flow_id", "=", self.id)]
        action["context"] = {
            "default_warehouse_id": self.warehouse_id.id,
            "default_flow_id": self.id,
        }
        return action

    def _generate_delivery_route(self):
        self.ensure_one()
        if self.delivery_route_id:
            return False
        vals = {
            "name": f"{self.warehouse_id.name}: {self.name}",
            "active": True,
            "product_categ_selectable": True,
            "warehouse_selectable": True,
            "product_selectable": False,
            "company_id": self.warehouse_id.company_id.id,
            "sequence": 10,
            "flow_id": self.id,
        }
        self.delivery_route_id = self.env["stock.location.route"].create(vals)

    def action_generate_routes(self):
        for flow in self:
            flow._generate_delivery_route()
        return True

    def _search_for_move_domain(self, move):
        return [
            ("from_picking_type_id", "=", move.picking_type_id.id),
            ("carrier_ids", "in", move.group_id.carrier_id.ids),
        ]

    @api.model
    def _search_for_move(self, move):
        """Return the first flow matching the move."""
        domain = self._search_for_move_domain(move)
        flow = self.search(domain)
        if flow and move.filtered_domain(safe_eval(flow.move_domain or "[]")):
            return flow
        return self.browse()

    def _apply_on_move(self, move):
        """Apply the flow configuration on the move."""
        logger.info("Applying flow '%s' on '%s'", self.name, move)
        move.picking_id = False
        move.picking_type_id = self.to_picking_type_id
        move.location_id = self.to_picking_type_id.default_location_src_id
        move._assign_picking()
