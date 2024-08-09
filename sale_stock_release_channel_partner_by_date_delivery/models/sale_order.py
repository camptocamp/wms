# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    release_channel_id = fields.Many2one(
        domain=(
            "carrier_id and "
            "['|', ('carrier_ids', '=', False), ('carrier_ids', 'in', [carrier_id])] "
            "or []"
        )
    )

    def _get_release_channel_id_depends(self):
        depends = super()._get_release_channel_id_depends()
        depends.append("carrier_id")
        return depends

    def _get_release_channel_partner_date_domain(self):
        domain = super()._get_release_channel_partner_date_domain()
        if self.carrier_id:
            domain.append(("release_channel_id.carrier_ids", "in", self.carrier_id.ids))
        return domain
