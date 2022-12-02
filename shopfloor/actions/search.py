# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class SearchResult:

    __slots__ = ("record", "type", "code")

    def __init__(self, **kw) -> None:
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def __bool__(self):
        return self.type != "none" or bool(self.record)

    def __eq__(self, other):
        for k in self.__slots__:
            if not hasattr(other, k):
                return False
            if getattr(other, k) != getattr(self, k):
                return False
        return True


class SearchAction(Component):
    """Provide methods to search records from scanner

    The methods should be used in Service Components, so a search will always
    have the same result in all scenarios.
    """

    _inherit = "shopfloor.search.action"

    # TODO: these methods shall be probably replaced by scan anything handlers

    def _parse_barcode_with_nomenclature(self, barcode_nom, barcode, types=None):
        # return barcode_nom.parse_barcode(barcode, types=types)
        return barcode_nom.parse_barcode(barcode)

    # TODO add configuration for barcodes nomenclatures
    #   => shopfloor.app + shopfloor.scenario + shopfloor.menu
    # To reduce overhead of searching with all possible nomenclatures, we would
    # like to limit the nomenclature to use for the search by configuration on
    # the Shopfloor app (global) and on the scenario.
    _nomenclatures = None

    @property
    def nomenclatures(self):
        if self._nomenclatures:
            return self._nomenclatures
        model = self.env["barcode.nomenclature"]
        nomenclatures = getattr(self.work, "barcode_nomemclatures", [])
        if not nomenclatures:
            nomenclatures = model.search([])
        self._nomenclatures = nomenclatures
        return nomenclatures

    @property
    def _barcode_type_handler(self):
        return {
            "product": self.product_from_scan,
            "package": self.package_from_scan,
            "picking": self.picking_from_scan,
            "location": self.location_from_scan,
            "location_dest": self.location_from_scan,
            "lot": self.lot_from_scan,
            "packaging": self.packaging_from_scan,
            "delivery_packaging": self.generic_packaging_from_scan,
        }

    def _make_search_result(self, **kwargs):
        """Build a 'SearchResult' object describing the record found.

        If no record has been found, the SearchResult object will have
        its 'type' defined to "none".
        """
        return SearchResult(**kwargs)

    def find(self, barcode, types=None, handler_kw=None):
        """Find Odoo record matching given `barcode`.

        Plain barcodes
        """
        res = None
        barcode = barcode or ""  # Nomenclature impl. doesn't support boolean values
        for nom in self.nomenclatures:
            res = self._find_record_by_nomenclature(
                barcode, nom, types=types, handler_kw=handler_kw
            )
            if res:
                return res
        # Fallback on plain barcode matching
        # TODO we should probably deprecate this and enforce having nomenclatures
        # for every kind of barcodes (even the simplest ones)
        # return self.generic_find(barcode, types=types, handler_kw=handler_kw)
        return self._make_search_result(type="none")

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

    def generic_find(self, barcode, types=None, handler_kw=None):
        handler_kw = handler_kw or {}
        _types = types or self._barcode_type_handler.keys()
        # TODO: decide the best default order in case we don't pass `types`
        for btype in _types:
            handler = self._barcode_type_handler[btype]
            record = handler(barcode, **handler_kw.get(btype, {}))
            if record:
                return self._make_search_result(record=record, code=barcode, type=btype)

        return self._make_search_result(type="none")

    def location_from_scan(self, barcode, limit=1):
        model = self.env["stock.location"]
        if not barcode:
            return model.browse()
        # First search location by barcode
        res = model.search([("barcode", "=", barcode)], limit=limit)
        # And only if we have not found through barcode search on the location name
        if len(res) < limit:
            res |= model.search([("name", "=", barcode)], limit=(limit - len(res)))
        return res

    def package_from_scan(self, barcode):
        model = self.env["stock.quant.package"]
        if not barcode:
            return model.browse()
        return model.search([("name", "=", barcode)], limit=1)

    def picking_from_scan(self, barcode):
        model = self.env["stock.picking"]
        if not barcode:
            return model.browse()
        return model.search([("name", "=", barcode)], limit=1)

    def product_from_scan(self, barcode, use_packaging=True):
        model = self.env["product.product"]
        if not barcode:
            return model.browse()
        product = model.search([("barcode", "=", barcode)], limit=1)
        if not product and use_packaging:
            packaging = self.packaging_from_scan(barcode)
            product = packaging.product_id
        return product

    def lot_from_scan(self, barcode, products=None, limit=1):
        model = self.env["stock.production.lot"]
        if not barcode:
            return model.browse()
        domain = [
            ("company_id", "=", self.env.company.id),
            ("name", "=", barcode),
        ]
        if products:
            domain.append(("product_id", "in", products.ids))
        return model.search(domain, limit=limit)

    def packaging_from_scan(self, barcode):
        model = self.env["product.packaging"]
        if not barcode:
            return model.browse()
        return model.search(
            [("barcode", "=", barcode), ("product_id", "!=", False)], limit=1
        )

    def generic_packaging_from_scan(self, barcode):
        model = self.env["product.packaging"]
        if not barcode:
            return model.browse()
        return model.search(
            [("barcode", "=", barcode), ("product_id", "=", False)], limit=1
        )
