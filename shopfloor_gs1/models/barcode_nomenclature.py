# Copyright 2022 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

# from odoo.exceptions import ValidationError
from ..utils import GS1Barcode


class BarcodeNomenclature(models.Model):
    _inherit = "barcode.nomenclature"

    is_gs1_nomenclature = fields.Boolean(
        string="Is GS1 Nomenclature",
        help="This Nomenclature use the GS1 specification, "
        "only GS1-128 encoding rules is accepted is this kind of nomenclature.",
    )

    def parse_barcode(self, barcode, ai_whitelist=None):
        if self.is_gs1_nomenclature:
            return self.parse_barcode_gs1(barcode, ai_whitelist=ai_whitelist)
        return super().parse_barcode(barcode)

    def parse_barcode_gs1(self, barcode, ai_whitelist=None):
        # TODO
        parsed = GS1Barcode.parse(barcode, ai_whitelist=ai_whitelist)
        res = []
        for item in parsed:
            # TODO: review v15 data mapping
            res.append(
                {
                    "rule": None,
                    "ai": item.ai,
                    "string_value": item.raw_value,
                    "value": item.value,
                    "type": item.type,
                }
            )
        return res
