# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockReleaseChannel(models.Model):

    _inherit = "stock.release.channel"

    def filter_release_channel_partner_window(self, partner):
        channels = self
        if (
            not partner.delivery_time_preference
            or partner.delivery_time_preference == "anytime"
        ):
            return channels

        for channel in self:
            if not channel.shipment_date:
                continue
            shipment_datetime = fields.Datetime.to_datetime(channel.shipment_date)
            if channel.process_end_date:
                shipment_datetime = shipment_datetime.replace(
                    hour=channel.process_end_date.hour,
                    minute=channel.process_end_date.minute,
                )
            if not partner.is_in_delivery_window(shipment_datetime):
                channels -= channel
        return channels
