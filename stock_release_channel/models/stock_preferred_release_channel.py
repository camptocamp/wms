# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockPreferredReleaseChannel(models.Model):
    _name = "stock.preferred.release.channel"
    _description = "Preferred Release Channel for a delivery address"
    _order = "date DESC"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        ondelete="cascade",
        string="Delivery Address",
        required=True,
        readonly=True,
        index=True,
    )
    release_channel_id = fields.Many2one(
        comodel_name="stock.release.channel",
        ondelete="cascade",
        string="Release Channel",
        required=True,
        index=True,
    )
    date = fields.Date(index=True)

    _sql_constraints = [
        (
            "uniq",
            "UNIQUE (partner_id, release_channel_id, date)",
            "A release channel for this date is already set.",
        ),
    ]

    @api.autovacuum
    def _gc_preferred_release_channels(self):
        pref_rcs = self.search(self._gc_preferred_release_channels_domain())
        pref_rcs.unlink()

    def _gc_preferred_release_channels_domain(self):
        return [("date", "<", fields.Date.today())]
