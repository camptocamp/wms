# Copyright 2022 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component

from ..utils import GS1Barcode


class SearchAction(Component):
    def find(self, barcode, types=None, handler_kw=None):
        barcode = barcode or ""
        res = self._find_gs1(barcode, types=types)
        if res:
            return res
        return super().find(barcode, types=types, handler_kw=handler_kw)

    def _find_gs1(self, barcode, types=None, handler_kw=None):
        types = types or ()
        ai_whitelist = [GS1Barcode.to_ai(x) for x in types]
        parsed = GS1Barcode.parse(barcode, ai_whitelist=ai_whitelist)
        if parsed:
            types = (parsed.type,)
        return self.generic_find(parsed.value, types=types, handler_kw=handler_kw)
