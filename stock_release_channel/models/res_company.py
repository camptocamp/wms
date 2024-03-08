# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    recompute_release_channel_after_released = fields.Boolean(
        string="Recompute Release Channel After Released",
        help="Will automatically recompute release channel on the picking after released",
        default=True
    )
