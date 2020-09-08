from odoo import fields, models


class StockPackageLevel(models.Model):
    _inherit = "stock.package_level"

    shopfloor_postponed = fields.Boolean(
        default=False,
        copy=False,
        help="Technical field. "
        "Indicates if a the package level has been postponed in a barcode scenario.",
    )

    def replace_package(self, new_package):
        """Replace a package on an assigned package level and related records

        The replacement package must have the same properties (same products
        and quantities).
        """
        if self.state not in ("new", "assigned"):
            return

        move_lines = self.move_line_ids
        # the write method on stock.move.line updates the reservation on quants
        move_lines.package_id = new_package
        # when a package is set on a line, the destination package is the same
        # by default
        move_lines.result_package_id = new_package
        for quant in new_package.quant_ids:
            for line in move_lines:
                if line.product_id == quant.product_id:
                    line.lot_id = quant.lot_id
                    line.owner_id = quant.owner_id

        self.package_id = new_package

    # TODO could be called when we write a different result package on line?
    def shallow_unlink(self):
        """Unlink package level without affecting moves and lines

        It still removes the result_package_id of related move lines,
        but *only* when it is the same package (prevent to remove a
        package changed manually).
        """
        if not self:
            return True
        for package_level in self:
            # We are no longer moving the entire package, match odoo's behavior
            # by emptying the result package, but keep it if it had a different
            # value set, because it means it has been set.
            lines = package_level.move_line_ids.filtered(
                lambda ml: ml.result_package_id == package_level.package_id
            )
            lines.result_package_id = False
        # when we unlink a package level, it automatically drops
        # any related move and resets the result_package_id of ALL
        # move lines, we prevent this by detaching it first
        self.write({"move_ids": [(6, 0, [])], "move_line_ids": [(6, 0, [])]})
        # as we are no longer moving an entire package, the
        # package level is irrelevant
        return self.unlink()
