# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import operator as py_operator

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import date_utils, float_compare, float_round

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    date_priority = fields.Datetime(
        string="Priority Date",
        index=True,
        default=fields.Datetime.now,
        help="Date/time used to sort moves to deliver first. "
        "Used to calculate the ordered available to promise.",
    )
    previous_promised_qty = fields.Float(
        string="Quantity Promised before this move",
        compute="_compute_previous_promised_qty",
        digits="Product Unit of Measure",
        help="Quantities promised to moves with higher priority than this move "
        "(in default UoM of the product).",
    )
    ordered_available_to_promise_qty = fields.Float(
        string="Ordered Available to Promise (Real Qty)",
        compute="_compute_ordered_available_to_promise",
        digits="Product Unit of Measure",
        help="Available to Promise quantity minus quantities promised "
        " to moves with higher priority (in default UoM of the product).",
    )
    ordered_available_to_promise_uom_qty = fields.Float(
        string="Ordered Available to Promise",
        compute="_compute_ordered_available_to_promise",
        search="_search_ordered_available_to_promise_uom_qty",
        digits="Product Unit of Measure",
        help="Available to Promise quantity minus quantities promised "
        " to moves with higher priority (in initial demand's UoM).",
    )
    release_ready = fields.Boolean(
        compute="_compute_release_ready",
        search="_search_release_ready",
    )
    need_release = fields.Boolean(index=True, copy=False)
    zip_code = fields.Char(related="partner_id.zip", store=True)
    city = fields.Char(related="partner_id.city", store=True)

    def _previous_promised_qty_sql_main_query(self):
        return """
            SELECT move.id,
                   COALESCE(SUM(previous_moves.previous_qty), 0.0)
            FROM stock_move move
            LEFT JOIN LATERAL (
                SELECT
                    m.product_qty
                    AS previous_qty
                FROM stock_move m
                INNER JOIN stock_location loc
                ON loc.id = m.location_id
                LEFT JOIN stock_picking_type p_type
                ON m.picking_type_id = p_type.id
                WHERE
                {lateral_where}
                GROUP BY m.id
            ) previous_moves ON true
            WHERE
            move.id IN %(move_ids)s
            GROUP BY move.id;
        """

    def _previous_promised_qty_sql_moves_before(self):
        sql = """
            m.priority > move.priority
            OR
            (
                m.priority = move.priority
                AND m.date_priority < move.date_priority
            )
            OR (
                m.priority = move.priority
                AND m.date_priority = move.date_priority
                AND m.picking_type_id = move.picking_type_id
                AND m.id < move.id
            )
            OR (
                m.priority = move.priority
                AND m.date_priority = move.date_priority
                AND m.picking_type_id != move.picking_type_id
                AND m.id > move.id
            )
        """
        return sql

    def _previous_promised_qty_sql_lateral_where(self):
        locations = self._ordered_available_to_promise_locations()
        sql = """
                m.id != move.id
                AND m.product_id = move.product_id
                AND p_type.code = 'outgoing'
                AND loc.parent_path LIKE ANY(%(location_paths)s)
                AND (
                    COALESCE(m.need_release, False) = COALESCE(move.need_release, False)
                    AND (
                        {moves_before}
                    )
                    OR (
                        move.need_release IS true
                        AND (m.need_release IS false OR m.need_release IS null)
                    )
                )
                AND m.state IN (
                    'waiting', 'confirmed', 'partially_available', 'assigned'
                )
        """.format(
            moves_before=self._previous_promised_qty_sql_moves_before()
        )
        params = {
            "location_paths": [
                "{}%".format(location.parent_path) for location in locations
            ]
        }
        horizon_date = self._promise_reservation_horizon_date()
        if horizon_date:
            sql += (
                " AND (m.need_release IS true AND m.date <= %(horizon)s "
                "      OR m.need_release IS false)"
            )
            params["horizon"] = horizon_date
        return sql, params

    def _previous_promised_qty_sql(self):
        """Lookup query for product promised qty in the same warehouse.

        Moves to consider are either already released or still be to released
        but not done yet. Each of them should fit the reservation horizon.
        """
        params = {"move_ids": tuple(self.ids)}
        lateral_where, lateral_params = self._previous_promised_qty_sql_lateral_where()
        params.update(lateral_params)
        query = self._previous_promised_qty_sql_main_query().format(
            lateral_where=lateral_where
        )
        return query, params

    @api.depends()
    def _compute_previous_promised_qty(self):
        if not self.ids:
            return
        self.flush()
        self.env["stock.move.line"].flush(["move_id", "product_qty"])
        self.env["stock.location"].flush(["parent_path"])
        self.previous_promised_qty = 0
        query, params = self._previous_promised_qty_sql()
        self.env.cr.execute(query, params)
        rows = dict(self.env.cr.fetchall())
        for move in self:
            move.previous_promised_qty = rows.get(move.id, 0)

    @api.depends(
        "ordered_available_to_promise_qty",
        "picking_id.move_type",
        "picking_id.move_lines",
        "need_release",
    )
    def _compute_release_ready(self):
        for move in self:
            if not move.need_release:
                move.release_ready = False
                continue
            if move.picking_id._get_shipping_policy() == "one":
                move.release_ready = move.picking_id.release_ready
            else:
                move.release_ready = move.ordered_available_to_promise_uom_qty > 0

    def _search_release_ready(self, operator, value):
        if operator != "=":
            raise UserError(_("Unsupported operator %s") % (operator,))
        moves = self.search([("ordered_available_to_promise_uom_qty", ">", 0)])
        moves = moves.filtered(lambda m: m.release_ready)
        return [("id", "in", moves.ids)]

    def _ordered_available_to_promise_locations(self):
        return self.env["stock.warehouse"].search([]).mapped("view_location_id")

    @api.depends()
    def _compute_ordered_available_to_promise(self):
        moves = self.filtered(
            lambda move: move._should_compute_ordered_available_to_promise()
        )
        (self - moves).update(
            {
                "ordered_available_to_promise_qty": 0.0,
                "ordered_available_to_promise_uom_qty": 0.0,
            }
        )

        locations = moves._ordered_available_to_promise_locations()

        # Compute On-Hand quantity (equivalent of qty_available) for all "view
        # locations" of all the warehouses: we may release as soon as we have
        # the quantity somewhere. Do not use "qty_available" to get a faster
        # computation.
        location_domain = []
        for location in locations:
            location_domain = expression.OR(
                [
                    location_domain,
                    [("location_id.parent_path", "=like", location.parent_path + "%")],
                ]
            )
        domain_quant = expression.AND(
            [[("product_id", "in", moves.product_id.ids)], location_domain]
        )
        location_quants = self.env["stock.quant"].read_group(
            domain_quant, ["product_id", "quantity"], ["product_id"], orderby="id"
        )
        quants_available = {
            item["product_id"][0]: item["quantity"] for item in location_quants
        }
        for move in moves:
            product_uom = move.product_id.uom_id
            previous_promised_qty = move.previous_promised_qty

            rounding = product_uom.rounding
            available_qty = float_round(
                quants_available.get(move.product_id.id, 0.0),
                precision_rounding=rounding,
            )

            real_promised = available_qty - previous_promised_qty
            uom_promised = product_uom._compute_quantity(
                real_promised,
                move.product_uom,
                rounding_method="HALF-UP",
            )

            move.ordered_available_to_promise_uom_qty = max(
                min(uom_promised, move.product_uom_qty),
                0.0,
            )
            move.ordered_available_to_promise_qty = max(
                min(real_promised, move.product_qty),
                0.0,
            )

    def _search_ordered_available_to_promise_uom_qty(self, operator, value):
        operator_mapping = {
            "<": py_operator.lt,
            "<=": py_operator.le,
            ">": py_operator.gt,
            ">=": py_operator.ge,
            "=": py_operator.eq,
            "!=": py_operator.ne,
        }
        if operator not in operator_mapping:
            raise UserError(_("Unsupported operator %s") % (operator,))
        moves = self.search([("need_release", "=", True)])
        operator_func = operator_mapping[operator]
        moves = moves.filtered(
            lambda m: operator_func(m.ordered_available_to_promise_uom_qty, value)
        )
        return [("id", "in", moves.ids)]

    def _should_compute_ordered_available_to_promise(self):
        return (
            self.picking_code == "outgoing"
            and not self.product_id.type == "consu"
            and not self.location_id.should_bypass_reservation()
        )

    def _action_cancel(self):
        super()._action_cancel()
        self.write({"need_release": False})
        return True

    def _promise_reservation_horizon(self):
        return self.env.company.sudo().stock_reservation_horizon

    def _promise_reservation_horizon_date(self):
        horizon = self._promise_reservation_horizon()
        if horizon:
            # start from end of today and add horizon days
            return date_utils.add(
                date_utils.end_of(fields.Datetime.today(), "day"), days=horizon
            )
        return None

    def release_available_to_promise(self):
        return self._run_stock_rule()

    def _prepare_move_split_vals(self, qty):
        vals = super()._prepare_move_split_vals(qty)
        # The method set procure_method as 'make_to_stock' by default on split,
        # but we want to keep 'make_to_order' for chained moves when we split
        # a partially available move in _run_stock_rule().
        if self.env.context.get("release_available_to_promise"):
            vals.update({"procure_method": self.procure_method, "need_release": True})
        return vals

    def _get_release_decimal_precision(self):
        return self.env["decimal.precision"].precision_get("Product Unit of Measure")

    def _get_release_remaining_qty(self):
        self.ensure_one()
        quantity = min(self.product_qty, self.ordered_available_to_promise_qty)
        remaining = self.product_qty - quantity
        precision = self._get_release_decimal_precision()
        if not float_compare(remaining, 0, precision_digits=precision) > 0:
            return
        return remaining

    def _is_releasable(self):
        self.ensure_one()
        if not self.need_release:
            return 0, 0
        if self.state not in ("confirmed", "waiting", "done", "cancel"):
            return 0, 0
        precision = self._get_release_decimal_precision()
        available_qty = self.ordered_available_to_promise_qty
        if float_compare(available_qty, 0, precision_digits=precision) <= 0:
            return 0, 0

        remaining_qty = self._get_release_remaining_qty()
        if remaining_qty:
            if self.picking_id._get_shipping_policy() == "one":
                # we don't want to deliver unless we can deliver all at
                # once
                return 0, 0
        return available_qty, remaining_qty

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        res["date_priority"] = self.date_priority
        return res

    def _run_stock_rule(self):
        """Launch procurement group run method with remaining quantity

        As we only generate chained moves for the quantity available minus the
        quantity promised to older moves, to delay the reservation at the
        latest, we have to periodically retry to assign the remaining
        quantities.
        """
        procurement_requests = []
        released_moves = self.env["stock.move"]
        for move in self:
            available_qty, remaining_qty = move._is_releasable()
            if not available_qty:
                continue
            if remaining_qty:
                move._release_split(remaining_qty)
            released_moves |= move

        # move the unreleased moves to a backorder
        released_pickings = released_moves.picking_id
        unreleased_moves = released_pickings.move_lines - released_moves
        unreleased_moves = unreleased_moves.filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        if unreleased_moves:
            unreleased_moves._unreleased_to_backorder()

        # pull the released moves
        for move in released_moves:
            move._before_release()
            values = move._prepare_procurement_values()
            procurement_requests.append(
                self.env["procurement.group"].Procurement(
                    move.product_id,
                    move.product_uom_qty,
                    move.product_uom,
                    move.location_id,
                    move.rule_id and move.rule_id.name or "/",
                    move.origin,
                    move.company_id,
                    values,
                )
            )
        self.env["procurement.group"].run_defer(procurement_requests)

        # Set all transfers released to "printed", consider the work has
        # been planned and started and another "release" of moves should
        # (for instance) merge new pickings with this "round of release".
        released_moves._after_release_assign_moves()
        released_moves._after_release_update_chain()

        return released_moves

    def _before_release(self):
        """Hook that aims to be overridden."""

    def _after_release_update_chain(self):
        picking_ids = set()
        moves = self
        while moves:
            picking_ids.update(moves.mapped("picking_id").ids)
            moves = moves.mapped("move_orig_ids")
        pickings = self.env["stock.picking"].browse(picking_ids)
        pickings._after_release_update_chain()
        # Set the highest priority on all pickings in the chain
        priorities = pickings.mapped("priority")
        if priorities:
            pickings.write({"priority": max(priorities)})

    def _after_release_assign_moves(self):
        moves = self
        while moves:
            moves._action_assign()
            moves = moves.mapped("move_orig_ids")

    def _release_split(self, remaining_qty):
        """Split move and put remaining_qty to a backorder move."""
        new_move_vals = self.with_context(release_available_to_promise=True)._split(
            remaining_qty
        )
        new_move = self.create(new_move_vals)
        new_move._action_confirm(merge=False)
        return new_move

    def _unreleased_to_backorder(self):
        """Move the unreleased moves to a new backorder picking"""
        # Rely on `printed` flag to make _assign_picking create a new picking.
        # See `stock.move._assign_picking` and
        # `stock.move._search_picking_for_assignation`.
        self.picking_id.write({"printed": True})
        origin_pickings = {m.id: m.picking_id for m in self}
        self._assign_picking()
        backorder_links = {}
        for move in self:
            origin = origin_pickings[move.id]
            if origin:
                backorder_links[move.picking_id] = origin
        for backorder, origin in backorder_links.items():
            backorder._release_link_backorder(origin)

    def _assign_picking_post_process(self, new=False):
        super()._assign_picking_post_process(new)
        priorities = self.mapped("move_dest_ids.picking_id.priority")
        if priorities:
            self.picking_id.write({"priority": max(priorities)})
