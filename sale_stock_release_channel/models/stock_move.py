# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        values = super()._get_new_picking_values()
        release_channel = self.group_id.release_channel_id
        if release_channel and self.picking_type_id.code == "outgoing":
            values["release_channel_id"] = release_channel.id
        return values

    def _key_assign_picking(self):
        keys = super()._key_assign_picking()
        return keys + (self.group_id.release_channel_id,)
