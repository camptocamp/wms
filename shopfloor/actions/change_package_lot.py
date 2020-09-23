from odoo import _

from odoo.addons.component.core import Component


class ChangePackageLot(Component):
    """Provide methods for changing a package or a lot on a move line"""

    _name = "shopfloor.change.package.lot.action"
    _inherit = "shopfloor.process.action"
    _usage = "change.package.lot"

    def change_lot(self, move_line, lot, response_ok_func, response_error_func):
        """Change the lot on the move line.

        :param response_ok_func: callable used to return ok response
        :param response_error_func: callable used to return error response
        """
        # If the lot is part of a package, what we really want
        # is not to change the lot, but change the package (which will
        # in turn change the lot altogether), but we have to pay attention
        # to some things:
        # * cannot replace a package by a lot without package (qty may be
        #   different, ...)
        # * if we have several packages for the same lot, we can't know which
        #   one the operator is moving, ask to scan a package
        lot_package_quants = self.env["stock.quant"].search(
            [
                ("lot_id", "=", lot.id),
                ("location_id", "=", move_line.location_id.id),
                ("package_id", "!=", False),
                ("quantity", ">", 0),
            ]
        )
        if move_line.package_id and not lot_package_quants:
            return response_error_func(
                move_line, message=self.msg_store.lot_is_not_a_package(lot),
            )
        if len(lot_package_quants) == 1:
            package = lot_package_quants.package_id
            return self.change_package(
                move_line, package, response_ok_func, response_error_func
            )
        elif len(lot_package_quants) > 1:
            return response_error_func(
                move_line,
                message=self.msg_store.several_packs_in_location(move_line.location_id),
            )
        return self._change_pack_lot_change_lot(
            move_line, lot, response_ok_func, response_error_func
        )

    def _change_pack_lot_change_lot(
        self, move_line, lot, response_ok_func, response_error_func
    ):
        inventory = self.actions_for("inventory")
        product = move_line.product_id
        if lot.product_id != product:
            return response_error_func(
                move_line, message=self.msg_store.lot_on_wrong_product(lot.name)
            )
        previous_lot = move_line.lot_id
        # Changing the lot on the move line updates the reservation on the quants
        move_line.lot_id = lot

        message = self.msg_store.lot_replaced_by_lot(previous_lot, lot)
        # check that we are supposed to have enough of this lot in the source location
        quant = lot.quant_ids.filtered(lambda q: q.location_id == move_line.location_id)
        if not quant:
            # not supposed to have this lot here... (if there is a quant
            # but not enough quantity we don't care here: user will report
            # a stock issue)
            inventory.create_control_stock(
                move_line.location_id,
                move_line.product_id,
                move_line.package_id,
                move_line.lot_id,
                _("Pick: stock issue on lot: {} found in {}").format(
                    lot.name, move_line.location_id.name
                ),
            )
            message["body"] += _(" A draft inventory has been created for control.")

        return response_ok_func(move_line, message=message)

    def _package_content_replacement_allowed(self, package, move_line):
        # we can't replace by a package which doesn't contain the product...
        return move_line.product_id in package.quant_ids.product_id

    def change_package(self, move_line, package, response_ok_func, response_error_func):
        inventory = self.actions_for("inventory")

        # prevent to replace a package by a package that would not satisfy the
        # move (different product)
        content_replacement_allowed = self._package_content_replacement_allowed(
            package, move_line
        )
        if not content_replacement_allowed:
            return response_error_func(
                move_line, message=self.msg_store.package_different_content(package)
            )

        previous_package = move_line.package_id

        if package.location_id != move_line.location_id:
            # the package has been scanned in the current location so we know its
            # a mistake in the data... fix the quant to move the package here
            inventory.move_package_quants_to_location(package, move_line.location_id)

        # search a package level which would already move the scanned package
        other_reserved_lines = self.env["stock.move.line"].search(
            [
                ("package_id", "=", package.id),
                ("state", "in", ("partially_available", "assigned")),
            ]
        )
        # think better! we can have another line using with a qty_done IF
        # the sum of qty_done + needed qty here is not > package qty
        # but in this case, we can't swap, we only have to use the package
        # we can't have another package level done because it moves everything
        # we can't have another line using it if the sum would be different
        # we can swap the packages, unless we have a qty_done already...
        # but if we swap and the other becomes unreserved?

        # total_qty_done = sum(other_reserved_lines.mapped("qty_done"))
        # package_quantity = sum(quants.mapped("quantity"))
        # quants = package.quant_ids.filtered(
        #     lambda quant: quant.product_id == move_line.product_id
        # )
        # if (total_qty_done + ) >
        # if any(line.qty_done > 0 for line in other_reserved_lines):
        #     return response_error_func(
        #         move_line,
        #         message=self.msg_store.package_already_picked_by(
        #             package, other_reserved_lines.picking_id
        #         ),
        #     )
        # we can't change already picked lines
        unreservable_lines = other_reserved_lines.filtered(
            lambda line: line.qty_done == 0
        )
        to_assign_moves = unreservable_lines.move_id
        # if we leave the package level, it will try to reserve the same
        # one again
        unreservable_lines.package_level_id.explode_package()
        unreservable_lines.unlink()

        move_line.replace_package(package)

        to_assign_moves._action_assign()

        # computation of the 'state' of the package levels is not
        # triggered, force it
        to_assign_moves.move_line_ids.package_level_id.modified(["move_line_ids"])
        move_line.package_level_id.modified(["move_line_ids"])

        return response_ok_func(
            move_line,
            message=self.msg_store.package_replaced_by_package(
                previous_package, package
            ),
        )
