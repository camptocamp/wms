from odoo import models


class StockPackageLevel(models.Model):
    _name = "stock.package_level"
    _inherit = ["stock.package_level", "shopfloor.priority.postpone.mixin"]

    def shallow_unlink(self):
        """Unlink but keep the moves"""
        self.move_ids.package_level_id = False
        self.unlink()

    def explode_package(self):
        move_lines = self.move_line_ids
        move_lines.result_package_id = False
        self.shallow_unlink()
