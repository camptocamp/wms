# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import date_utils, float_compare

from odoo.addons import decimal_precision as dp


class StockMove(models.Model):
    _inherit = "stock.move"

    date_priority = fields.Datetime(
        string="Priority Date",
        index=True,
        default=fields.Datetime.now,
        help="Date/time used to sort moves to deliver first. "
        "Used to calculate the ordered available to promise.",
    )
    ordered_available_to_promise = fields.Float(
        string="Ordered Available to Promise",
        compute="_compute_ordered_available_to_promise",
        digits=dp.get_precision("Product Unit of Measure"),
        help="Available to Promise quantity minus quantities promised "
        " to older promised operations.",
    )
    need_release = fields.Boolean()

    @api.depends()
    def _compute_ordered_available_to_promise(self):
        for move in self:
            move.ordered_available_to_promise = move._ordered_available_to_promise()

    def _should_compute_ordered_available_to_promise(self):
        return (
            self.picking_code == "outgoing"
            and self.need_release
            and not self.product_id.type == "consu"
            and not self.location_id.should_bypass_reservation()
        )

    def _action_cancel(self):
        super()._action_cancel()
        self.write({"need_release": False})
        return True

    def _ordered_available_to_promise(self):
        if not self._should_compute_ordered_available_to_promise():
            return 0.0
        available = self.product_id.with_context(
            **self._order_available_to_promise_qty_ctx()
        ).qty_available
        return max(
            min(available - self._previous_promised_qty(), self.product_qty), 0.0
        )

    def _order_available_to_promise_qty_ctx(self):
        return {
            # used by product qty calculation in stock module
            # (all the way down to `_get_domain_locations`).
            "location": self.warehouse_id.lot_stock_id.id,
        }

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

    def _previous_promised_quantity_domain(self):
        """Lookup for product promised qty in the same warehouse.

        Moves to consider are either already released or still be to released
        but not done yet. Each of them should fit the reservation horizon.
        """
        base_domain = [
            ("product_id", "=", self.product_id.id),
            ("warehouse_id", "=", self.warehouse_id.id),
        ]
        horizon_date = self._promise_reservation_horizon_date()
        if horizon_date:
            # exclude moves planned beyond the horizon
            base_domain.append(("date_expected", "<=", horizon_date))

        # either the move has to be released
        # and priority is higher than the current one
        domain_not_released = [
            ("need_release", "=", True),
            ("date_priority", "<", self.date_priority),
        ]
        # or it has been released already
        # and the picking is printed
        # and is not canceled or done
        domain_released = [
            ("need_release", "=", False),
            ("picking_id.printed", "=", True),
            (
                "state",
                "in",
                ("waiting", "confirmed", "partially_available", "assigned"),
            ),
        ]
        return expression.AND(
            [base_domain, expression.OR([domain_not_released, domain_released])]
        )

    def _previous_promised_qty(self):
        previous_moves = self.search(
            expression.AND(
                # TODO: `!=` is suboptimal, consider filter out on recordset
                [self._previous_promised_quantity_domain(), [("id", "!=", self.id)]]
            ),
        )
        promised_qty = sum(
            previous_moves.mapped(
                lambda move: max(move.product_qty - move.reserved_availability, 0.0)
            )
        )
        return promised_qty

    def release_available_to_promise(self):
        self._run_stock_rule()

    def _prepare_move_split_vals(self, qty):
        vals = super()._prepare_move_split_vals(qty)
        # The method set procure_method as 'make_to_stock' by default on split,
        # but we want to keep 'make_to_order' for chained moves when we split
        # a partially available move in _run_stock_rule().
        if self.env.context.get("release_available_to_promise"):
            vals.update({"procure_method": self.procure_method, "need_release": True})
        return vals

    def _run_stock_rule(self):
        """Launch procurement group run method with remaining quantity

        As we only generate chained moves for the quantity available minus the
        quantity promised to older moves, to delay the reservation at the
        latest, we have to periodically retry to assign the remaining
        quantities.
        """
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        procurement_requests = []
        pulled_moves = self.env["stock.move"]
        for move in self:
            if not move.need_release:
                continue
            if move.state not in ("confirmed", "waiting"):
                continue
            # do not use the computed field, because it will keep
            # a value in cache that we cannot invalidate declaratively
            available_quantity = move._ordered_available_to_promise()
            if float_compare(available_quantity, 0, precision_digits=precision) <= 0:
                continue

            quantity = min(move.product_qty, available_quantity)
            remaining = move.product_qty - quantity

            if float_compare(remaining, 0, precision_digits=precision) > 0:
                if move.picking_id.move_type == "one":
                    # we don't want to deliver unless we can deliver all at
                    # once
                    continue
                move.with_context(release_available_to_promise=True)._release_split(
                    remaining
                )

            if not move.picking_id.printed:
                # Make sure the flag is set even if no split happens.
                move.picking_id.printed = True

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
            pulled_moves |= move

        self.env["procurement.group"].run_defer(procurement_requests)

        while pulled_moves:
            pulled_moves._action_assign()
            pulled_moves = pulled_moves.mapped("move_orig_ids")

        return True

    def _release_split(self, remaining_qty):
        """Split move and create a new picking for it.

        Instead of splitting the move and leave remaining qty into the same picking
        we move it to a new one so that we can release it later as soon as
        the qty is available.
        """
        # Rely on `printed` flag to make _assign_picking create a new picking.
        # See `stock.move._assign_picking` and
        # `stock.move._search_picking_for_assignation`.
        if not self.picking_id.printed:
            self.picking_id.printed = True
        new_move = self.browse(self._split(remaining_qty))
        # Picking assignment is needed here because `_split` copies the move
        # thus the `_should_be_assigned` condition is not satisfied
        # and the move is not assigned.
        new_move._assign_picking()
        return new_move
