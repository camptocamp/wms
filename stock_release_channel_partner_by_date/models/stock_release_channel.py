# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockReleaseChannel(models.Model):
    _inherit = "stock.release.channel"

    def action_sleep(self):
        res = super().action_sleep()
        channel_dates = self.env["stock.release.channel.partner.date"].search(
            self._get_release_channel_partner_date_domain()
        )
        channel_dates.write({"active": False})
        return res

    def _get_release_channel_partner_date_domain(self):
        return [("release_channel_id", "in", self.ids)]
