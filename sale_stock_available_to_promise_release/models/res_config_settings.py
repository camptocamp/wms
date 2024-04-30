# Copyright 2023 Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    display_is_available = fields.Boolean(
        related="company_id.display_is_available",
        help="Show Available column in SO and quotation reports",
        readonly=False,
    )
