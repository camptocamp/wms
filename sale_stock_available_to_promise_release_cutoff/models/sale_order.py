# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("order_line.availability_status", "picking_policy")
    def _compute_display_expected_date_ok(self):
        """Conditions to display the expected date on the sale_order report.

        Displayed if:
            - date is set (defined in sale_stock_available_to_promise_release)
            - policy is 'when all products are ready' and everything is available
            - policy is 'as soon as possible' and at least one line is available
        """
        super()._compute_display_expected_date_ok()
        for record in self:
            lines = record.order_line.filtered(
                lambda l: not l.is_delivery and not l.display_type
            )
            policy_availability = (
                lines._all_lines_available() and record.picking_policy == "one"
            ) or (lines._any_line_available() and record.picking_policy == "direct")
            record.display_expected_date_ok = (
                record.display_expected_date_ok and policy_availability
            )
