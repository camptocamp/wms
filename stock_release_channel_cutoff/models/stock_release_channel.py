# Copyright 2023 Camptocamp
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime, timedelta

import pytz

from odoo import api, fields, models

from odoo.addons.stock_release_channel import delivery_date_generator
from odoo.addons.stock_release_channel_process_end_time.utils import (
    float_to_time,
    time_to_datetime,
)


class StockReleaseChannel(models.Model):
    _inherit = "stock.release.channel"

    cutoff_time = fields.Float(
        help="Fill in this to warning on kanban view if the current time "
        "becomes the cutoff time."
    )
    # Technical field for warning on kanban view
    cutoff_warning = fields.Boolean(compute="_compute_cutoff_warning")

    @property
    def cutoff_datetime(self):
        self.ensure_one()
        if not self.cutoff_time:
            return False
        now = self.process_end_date if self.state == "open" else fields.Datetime.now()
        return time_to_datetime(
            float_to_time(
                self.cutoff_time,
            ),
            now=now,
            tz=self.process_end_time_tz,
        )

    @api.depends("cutoff_time", "state", "process_end_date", "process_end_time_tz")
    def _compute_cutoff_warning(self):
        now = fields.Datetime.now()
        for channel in self:
            cutoff_warning = False
            if channel.state == "open" and channel.cutoff_time:
                cutoff_warning = channel.cutoff_datetime < now
            channel.cutoff_warning = cutoff_warning

    @delivery_date_generator(step="preparation")
    def _next_delivery_date_cutoff(self, delivery_date, partner=None):
        """Get the next valid delivery date respecting cutoff.

        The preparation date must be before the cutoff time otherwise it is
        postponed to next day.

        A delivery date generator needs to provide the earliest valid date
        starting from the received date. It can be called multiple times with a
        new date to validate.
        """
        self.ensure_one()
        cutoff = self.cutoff_datetime
        if not cutoff:
            # any date is valid
            while True:
                delivery_date = yield delivery_date
        wh_tz = pytz.timezone(self.process_end_time_tz)
        next_day = time_to_datetime(
            datetime.min.time(),
            now=cutoff + timedelta(days=1),
            tz=wh_tz,
        )
        while True:
            while delivery_date <= cutoff:
                delivery_date = yield delivery_date
            delivery_date = yield max(delivery_date, next_day)
