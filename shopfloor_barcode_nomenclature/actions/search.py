# Copyright 2022 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component

# TODO: tests


class SearchAction(Component):
    def _get_default_nomenclatures(self):
        model = self.env["barcode.nomenclature"]
        return (
            # check if we gave menu
            self.collection.barcode_nomenclature_ids
            or self._menu.barcode_nomenclature_ids
            or model.search([])
        )

    def _parse_barcode_with_nomenclature(self, barcode_nom, barcode, types=None):
        # return barcode_nom.parse_barcode(barcode, types=types)
        return barcode_nom.parse_barcode(barcode)

    _nomenclatures = None

    @property
    def nomenclatures(self):
        if self._nomenclatures:
            return self._nomenclatures
        nomenclatures = getattr(self.work, "barcode_nomenclatures", [])
        if not nomenclatures:
            nomenclatures = self._get_default_nomenclatures()
        self._nomenclatures = nomenclatures
        return nomenclatures

    def find(self, barcode, types=None, handler_kw=None):
        res = None
        barcode = barcode or ""  # Nomenclature impl. doesn't support boolean values
        for nom in self.nomenclatures:
            res = self._find_record_by_nomenclature(
                barcode, nom, types=types, handler_kw=handler_kw
            )
            if res:
                return res
        return super().find(barcode, types=types, handler_kw=handler_kw)

    def _find_record_by_nomenclature(
        self, barcode, nomenclature, types=None, handler_kw=None
    ):
        handler_kw = handler_kw or {}
        if nomenclature:
            info = self._parse_barcode_with_nomenclature(
                nomenclature, barcode, types=types
            )
            btype = info["type"]
            # NOTE if nomenclature finds nothing it returns type=error
            # then we won't find an handler for it.
            # But if a rule matches the barcode (a wildcard one like 'product')
            # it will return a type="something" but this only means that the
            # barcode has matched one rule, not that a record has been found.
            handler = self._barcode_type_handler.get(btype)
            if handler:
                record = handler(info["code"], **handler_kw.get(btype, {}))
                if not record:
                    return self._make_search_result(type="none")
                info["record"] = record
                return self._make_search_result(**info)
        return self._make_search_result(type="none")
