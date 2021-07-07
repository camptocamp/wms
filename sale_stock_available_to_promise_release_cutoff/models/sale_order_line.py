# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _all_lines_available(self):
        for line in self:
            if line.availability_status != "full":
                return False
        return True

    def _any_line_available(self):
        for line in self:
            if line.availability_status == "full":
                return True
        return False
