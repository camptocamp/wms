# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class MrpProductProduce(models.Model):
    _inherit = "mrp.production"

    # def subcontracting_record_component(self):
    #     # Overridden to unlink existing move lines on the finished product to
    #     # receive when the components consumption is recorded. As a result we
    #     # will get only new move lines related to the production, avoiding
    #     # issues when processing them with the reception screen.
    #     dest_moves = self.move_finished_ids.move_dest_ids.filtered(
    #         lambda m: m.state not in ("done", "cancel")
    #     )
    #     incoming = "incoming" in dest_moves.mapped("picking_code")
    #     if incoming:
    #         dest_moves._do_unreserve()
    #     res = super().subcontracting_record_component()
    #     if incoming:
    #         dest_moves._action_assign()
    #     return res
