# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockReleaseChannel(models.Model):
    _inherit = "stock.release.channel"

    delivery_weekday_ids = fields.Many2many(
        "time.weekday",
        "release_channel_delivery_weekday_rel",
        "channel_id",
        "weekday_id",
        string="Delivery weekdays",
    )
    preparation_weekday_ids = fields.Many2many(
        "time.weekday",
        compute="_compute_preparation_weekday_ids",
        readonly=True,
        store=True,
    )

    @api.depends("delivery_weekday_ids", "shipment_lead_time")
    def _compute_preparation_weekday_ids(self):
        for channel in self:
            weekday_names = []
            delivery_weekdays = channel.delivery_weekday_ids
            for wd in delivery_weekdays:
                wd_minus_lead = int(wd.name) - channel.shipment_lead_time
                if wd_minus_lead < 0:
                    while not 0 <= wd_minus_lead < 7:
                        wd_minus_lead += 7
                weekday_names.append(str(wd_minus_lead))
            channel.preparation_weekday_ids = self.env["time.weekday"].search(
                [("name", "in", weekday_names)]
            )
