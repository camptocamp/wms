# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ShopfloorWorkstation(models.Model):
    _name = "shopfloor.workstation"
    _description = "Shopfloor workstation settings"

    name = fields.Char(required=True)
    barcode = fields.Char(required=True, index=True, copy=False)
    active = fields.Boolean(default=True)
    printing_printer_id = fields.Many2one(
        comodel_name="printing.printer", string="Standard Printer"
    )
    # TODO move to related local module
    # label_printer_id = fields.Many2one(
    #     comodel_name="printing.printer", string="Label Printer"
    # )
    shopfloor_profile_id = fields.Many2one(
        comodel_name="shopfloor.profile", string="Shopfloor Profile"
    )
