# Copyright 2023 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import api, fields, models


class StockReleaseChannel(models.Model):
    _inherit = "stock.release.channel"

    cutoff_datetime = fields.Datetime()
    cutoff_time = fields.Char(compute="_compute_cutoff_time")

    @api.depends("cutoff_datetime")
    def _compute_cutoff_time(self):
        for rec in self:
            if rec.cutoff_datetime:
                context_dt = fields.Datetime.context_timestamp(rec, rec.cutoff_datetime)
                rec.cutoff_time = context_dt.strftime("%H:%M")
            else:
                rec.cutoff_time = False
