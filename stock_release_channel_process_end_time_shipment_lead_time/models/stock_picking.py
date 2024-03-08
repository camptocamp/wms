# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _search_scheduled_date_prior_to_channel_end_date_condition(self):
        self.env["stock.release.channel"].flush_model(
            ["process_end_date", "shipment_date", "shipment_lead_time"]
        )
        self.env["stock.picking"].flush_model(["scheduled_date"])
        end_date = "stock_release_channel.shipment_date"
        # We don't consider warehouse calendar when there is no process end date
        lead_time = (
            "interval '1 day' * coalesce(stock_release_channel.shipment_lead_time, 0)"
        )
        cond = f"""
            CASE WHEN stock_release_channel.process_end_date is not null
            THEN date(stock_picking.scheduled_date at time zone 'UTC' at time zone wh.tz)
            < {end_date} + interval '1 day'
            ELSE date(stock_picking.scheduled_date at time zone 'UTC' at time zone wh.tz)
            < date(now() at time zone wh.tz) + {lead_time} + interval '1 day'
            END
        """
        return cond
