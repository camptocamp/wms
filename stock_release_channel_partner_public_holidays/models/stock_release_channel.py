# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockReleaseChannel(models.Model):

    _inherit = "stock.release.channel"

    exclude_public_holidays = fields.Boolean()

    def filter_release_channel(self, partner):
        channels = self
        for channel in self:
            if not channel.exclude_public_holidays:
                continue
            if channel._is_shipment_date_a_public_holiday(partner):
                channels -= channel
        return channels

    def _is_shipment_date_a_public_holiday(self, partner):
        """
        Returns True if shipment_date is a public holiday
        :return: bool
        """
        self.ensure_one()
        res = False
        shipment_date = self.shipment_date
        if not shipment_date:
            return res
        holidays_filter = [("year", "=", shipment_date.year)]
        if partner:
            if partner.country_id:
                holidays_filter.append("|")
                holidays_filter.append(("country_id", "=", False))
                holidays_filter.append(("country_id", "=", partner.country_id.id))
            else:
                holidays_filter.append(("country_id", "=", False))
        pholidays = self.env["hr.holidays.public"].search(holidays_filter)
        if not pholidays:
            return res

        states_filter = [("year_id", "in", pholidays.ids)]
        if partner.state_id:
            states_filter += [
                "|",
                ("state_ids", "=", False),
                ("state_ids", "=", partner.state_id.id),
            ]
        else:
            states_filter.append(("state_ids", "=", False))
        states_filter.append(("date", "=", shipment_date))
        hhplo = self.env["hr.holidays.public.line"]
        holidays_line = hhplo.search(states_filter, limit=1)
        return bool(holidays_line)
