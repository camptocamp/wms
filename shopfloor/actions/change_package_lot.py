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

    def _package_replacement_allowed(self, package, move_lines):
        package_products = package.quant_ids.product_id
        line_products = move_lines.product_id
        # If some products of the lines are not in the replacement
        # package, we can't allow the replacement.
        # If the package has *more* products though, we can do it
        # and the operator will have to move them out of the package.
        return not (line_products - package_products)

    def change_package(self, move_line, package, response_ok_func, response_error_func):
        inventory = self.actions_for("inventory")

        package_level = move_line.package_level_id
        # several move lines can be moved by the package level, we'll have
        # to update all of them
        move_lines = package_level.move_line_ids

        # prevent to replace a package by a package that would not satisfy the
        # move (different product)
        replacement_allowed = self._package_replacement_allowed(package, move_lines)
        if not replacement_allowed:
            return response_error_func(
                move_line, message=self.msg_store.package_different_content(package)
            )

        previous_package = move_line.package_id

        if package.location_id != move_line.location_id:
            # the package has been scanned in the current location so we know its
            # a mistake in the data... fix the quant to move the package here
            inventory.move_package_quants_to_location(package, move_line.location_id)

        import ipdb; ipdb.set_trace()

        # search a package level which would already move the scanned package
        other_reserved_lines = (
            self.env["stock.move.line"].search(
                [
                    ("package_id", "=", package.id),
                    ("state", "in", ("partially_available", "assigned")),
                ])
        )
        # think better! we can have another line using with a qty_done IF
        # the sum of qty_done + needed qty here is not > package qty
        # but in this case, we can't swap, we only have to use the package
        # we can't have another package level done because it moves everything
        # we can't have another line using it if the sum would be different
        # we can swap the packages, unless we have a qty_done already...
        # but if we swap and the other becomes unreserved?

        if any(line.qty_done > 0 for line in other_reserved_lines):
            return response_error_func(
                move_line,
                message=self.msg_store.package_already_picked_by(
                    package, other_reserved_lines.picking_id
                ),
            )

        # TODO we do not have a package level if we have a partial package reserved
        # Switch the package with the level which was moving it, as we know
        # that:
        # * only one package level at a time is supposed to move a package
        # * the content of the other package contains the same product
        # * if we left the reserved level with the scanned package, we would
        #   have 2 levels for the same package and odoo would unreserve the
        #   move lines as soon as we confirm the current moves
        # Considering this, we should be safe to interchange the packages
        if reserved_level:
            # Ignore updates on quant reservation, which would prevent to switch
            # 2 packages between 2 assigned package levels: when writing the
            # package of the second level to the first level, it would unreserve
            # it because the second level is still using the package.
            # But here, we know they both available before and must be available after!
            reserved_level.with_context(bypass_reservation_update=True).replace_package(
                previous_package
            )
            package_level.with_context(bypass_reservation_update=True).replace_package(
                package
            )
        else:
            # when we are not switching packages, we expect the quant
            # reservations to be aligned
            package_level.replace_package(package)

        return response_ok_func(
            move_line,
            message=self.msg_store.package_replaced_by_package(
                previous_package, package
            ),
        )
