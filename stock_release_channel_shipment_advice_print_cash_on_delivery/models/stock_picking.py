# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    cash_on_delivery_invoice_ids = fields.Many2many(
        "account.move", string="COD Invoices", copy=False, readonly=True
    )

    def _action_done(self):
        res = super()._action_done()
        for rec in self:
            sales = rec.move_ids.filtered(
                lambda move: move.state == "done"
                and not move.location_dest_id.scrap_location
                and move.location_dest_id.usage == "customer"
            ).mapped("sale_line_id.order_id")
            cash_on_delivery_sales = sales.filtered(
                lambda sale: sale.payment_term_id.cash_on_delivery
            )
            if cash_on_delivery_sales:
                invoices = cash_on_delivery_sales._create_invoices(final=True)
                if invoices:
                    # Validate invoices
                    invoices.action_post()
                    rec.cash_on_delivery_invoice_ids = invoices
        return res
