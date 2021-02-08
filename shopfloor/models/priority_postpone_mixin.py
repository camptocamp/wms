# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class PriorityPostponeMixin(models.AbstractModel):
    _name = "shopfloor.priority.postpone.mixin"
    _description = "Adds shopfloor priority/postpone fields"

    _SF_PRIORITY_DEFAULT = 10

    shopfloor_priority = fields.Integer(
        default=lambda self: self._SF_PRIORITY_DEFAULT,
        copy=False,
        help="Technical field. Overrides operation priority in barcode scenario.",
    )
    shopfloor_postponed = fields.Boolean(
        copy=False,
        help="Technical field. "
        "Indicates if the operation has been postponed in a barcode scenario.",
    )

    def _get_max_shopfloor_priority(self, records):
        self.ensure_one()
        return max(rec.shopfloor_priority for rec in records)

    def shopfloor_postpone(self, records):
        """Postpone the record and update its priority based on other records."""
        self.ensure_one()
        # Set the max priority from sibling records + 1
        max_priority = self._get_max_shopfloor_priority(records)
        self.shopfloor_priority = max_priority + 1
        self.shopfloor_postponed = True
