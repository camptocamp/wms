# Copyright 2022 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ShopfloorMenu(models.Model):
    _inherit = "shopfloor.menu"

    barcode_nomenclature_ids = fields.Many2many(
        string="Barcode nomenclatures",
        comodel_name="barcode.nomenclature",
    )
