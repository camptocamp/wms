from odoo import fields, models

from .stock_move_line import StockMoveLine


class StockPackageLevel(models.Model):
    _inherit = "stock.package_level"

    # shopfloor_priority is set to this value when postponed
    # consider it as the max value for priority
    _SF_PRIORITY_POSTPONED = StockMoveLine._SF_PRIORITY_POSTPONED

    shopfloor_priority = fields.Integer(
        default=10,
        copy=False,
        help="Technical field. "
        "Overrides package level's priority in barcode scenario.",
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
