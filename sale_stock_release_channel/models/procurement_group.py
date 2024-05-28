# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    release_channel_id = fields.Many2one(
        comodel_name="stock.release.channel",
        string="Release Channel"
    )
