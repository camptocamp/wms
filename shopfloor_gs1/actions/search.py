# Copyright 2022 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class SearchAction(Component):
    def _get_default_nomenclatures(self):
        return (
            self.collection.barcode_nomenclature_ids
            or self._menu.barcode_nomenclature_ids
            or super()._get_default_nomenclatures()
        )
