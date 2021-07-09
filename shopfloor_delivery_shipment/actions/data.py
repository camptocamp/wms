# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component
from odoo.addons.shopfloor_base.utils import ensure_model


class DataAction(Component):
    _inherit = "shopfloor.data.action"

    @ensure_model("shipment.advice")
    def shipment_advice(self, record, **kw):
        return self._jsonify(
            record.with_context(shipment_advice=record.id),
            self._shipment_advice_parser,
            **kw
        )

    def shipment_advices(self, record, **kw):
        return self.shipment_advice(record, multi=True)

    @property
    def _shipment_advice_parser(self):
        return [
            "id",
            "name",
            "state",
        ]

    @ensure_model("stock.dock")
    def dock(self, record, **kw):
        return self._jsonify(
            record.with_context(dock=record.id), self._dock_parser, **kw
        )

    def docks(self, record, **kw):
        return self.dock(record, multi=True)

    @property
    def _dock_parser(self):
        return [
            "id",
            "name",
        ]
