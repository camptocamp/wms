# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo import models

from odoo.addons.stock_release_channel import decorators

_logger = logging.getLogger(__name__)


class StockReleaseChannel(models.Model):
    _inherit = "stock.release.channel"

    def _get_best_delivery_date(self, partner, order_dt):
        """Compute the earliest delivery date for this channel

        Go through each steps. All generators of a step must agree on a date.
        Initialize them with the provided start date for the first step and
        then with the agreed date from the previous step. If a generator
        provides a later date, send that date to the other generators to
        request agreement or a new later date.
        This algorithm performs a quick convergence to a date.
        """
        self.ensure_one()
        best_dt = order_dt
        for step in decorators.delivery_date_steps:
            funcs = decorators.delivery_date_generators.get(step)
            if not funcs:
                continue
            generators = []
            best_generators = []
            start_dt = best_dt
            for func in funcs:
                # initialize generators with the start date
                gen = func(self, start_dt, partner)
                generators.append(gen)
                new_dt = next(gen)
                if new_dt > best_dt:
                    best_dt = new_dt
                    best_generators = [gen]
                elif new_dt == best_dt:
                    best_generators.append(gen)
            # loop until all generators return the same last date
            while len(generators) != len(best_generators):
                for gen in generators:
                    if gen in best_generators:
                        continue
                    best_dt = gen.send(previous_dt := best_dt)
                    if best_dt != previous_dt:
                        best_generators = [gen]
                    else:
                        best_generators.append(gen)
            for gen in generators:
                gen.close()
        return best_dt
