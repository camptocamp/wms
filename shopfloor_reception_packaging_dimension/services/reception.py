# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.addons.shopfloor.utils import to_float


class Reception(Component):
    _inherit = "shopfloor.reception"

    def _before_response_for_set_quantity(self, picking, line):
        """Show the packaging dimension screen before the set quantity screen."""
        if not self.work.menu.set_packaging_dimension:
            return self._response_for_set_quantity(picking, line)
        packaging = self._get_next_packaging_to_set_dimension(line.product_id)
        if packaging:
            return self._response_for_set_packaging_dimension(picking, line, packaging)
        return self._response_for_set_quantity(picking, line)

    def _get_next_packaging_to_set_dimension(self, product, previous_packaging=None):
        """Return for a product the next packaging needing dimension to be set."""
        next_packaging_id = previous_packaging.id + 1 if previous_packaging else 0
        domain = [
            ("product_id", "=", product.id),
            ("id", ">=", next_packaging_id),
            "|",
            "|",
            "|",
            "|",
            "|",
            "|",
            "|",
            "|",
            "|",
            "|",
            ("packaging_length", "=", 0),
            ("packaging_length", "=", False),
            ("width", "=", 0),
            ("width", "=", False),
            ("height", "=", 0),
            ("height", "=", False),
            ("max_weight", "=", 0),
            ("max_weight", "=", False),
            ("qty", "=", 0),
            ("qty", "=", False),
            ("barcode", "=", False),
        ]
        return self.env["product.packaging"].search(domain, order="id", limit=1)

    def _response_for_set_packaging_dimension(
        self, picking, line, packaging=None, message=None
    ):
        if not packaging:
            packaging = self._get_next_packaging_to_set_dimension(line.product_id)
        if not packaging:
            return self._response_for_set_quantity(picking, line, message=message)
        return self._response(
            next_state="set_packaging_dimension",
            data={
                "picking": self.data.picking(picking),
                "selected_move_line": self.data.move_line(line),
                "packaging": self.data_detail.packaging_detail(packaging),
            },
            message=message,
        )

    def set_packaging_dimension(
        self,
        picking_id,
        selected_line_id,
        packaging_id,
        height=None,
        length=None,
        width=None,
        weight=None,
        qty=None,
        barcode=None,
        cancel=False,
    ):
        """Set the dimension on a product packaging.

        If the user cancel the dimension update we still propose the next
        possible packgaging.

        Transitions:
            - set_packaging_dimension: if more packaging needs dimension
            - set_quantity: otherwise
        """
        picking = self.env["stock.picking"].browse(picking_id)
        selected_line = self.env["stock.move.line"].browse(selected_line_id)
        packaging = self.env["product.packaging"].sudo().browse(packaging_id)
        message = None
        next_packaging = None
        if not packaging:
            message = self.msg_store.record_not_found()
        elif (height or length or width or weight or barcode or qty) and not cancel:
            if height:
                packaging.height = height
            if length:
                packaging.packaging_length = length
            if width:
                packaging.width = width
            if weight:
                packaging.max_weight = weight
            if barcode:
                packaging.barcode = barcode
            if qty:
                packaging.qty = qty
            message = self.msg_store.packaging_dimension_updated(packaging)
        if packaging:
            next_packaging = self._get_next_packaging_to_set_dimension(
                selected_line.product_id, packaging
            )
        if not next_packaging:
            return self._response_for_set_quantity(
                picking, selected_line, message=message
            )
        return self._response_for_set_packaging_dimension(
            picking, selected_line, next_packaging, message=message
        )

    class ShopfloorReceptionValidator(Component):
        _inherit = "shopfloor.reception.validator"

        def set_packaging_dimension(self):
            return {
                "picking_id": {"coerce": to_int, "required": True, "type": "integer"},
                "selected_line_id": {
                    "coerce": to_int,
                    "required": True,
                    "type": "integer",
                },
                "packaging_id": {"coerce": to_int, "required": True, "type": "integer"},
                "height": {
                    "coerce": to_float,
                    "required": False,
                    "type": "float",
                    "nullable": True,
                },
                "length": {
                    "coerce": to_float,
                    "required": False,
                    "type": "float",
                    "nullable": True,
                },
                "width": {
                    "coerce": to_float,
                    "required": False,
                    "type": "float",
                    "nullable": True,
                },
                "weight": {
                    "coerce": to_float,
                    "required": False,
                    "type": "float",
                    "nullable": True,
                },
                "shipping_weight": {
                    "coerce": to_float,
                    "required": False,
                    "type": "float",
                    "nullable": True,
                },
                "qty": {
                    "coerce": to_float,
                    "required": False,
                    "type": "float",
                    "nullable": True,
                },
                "barcode": {"type": "string", "required": False, "nullable": True},
                "cancel": {"type": "boolean"},
            }


class ShopfloorReceptionValidatorResponse(Component):
    _inherit = "shopfloor.reception.validator.response"

    def _states(self):
        res = super()._states()
        res.update({"set_packaging_dimension": self._schema_set_packaging_dimension})
        return res

    def _scan_line_next_states(self):
        res = super()._scan_line_next_states()
        res.update({"set_packaging_dimension"})
        return res

    def _set_lot_confirm_action_next_states(self):
        res = super()._set_lot_confirm_action_next_states()
        res.update({"set_packaging_dimension"})
        return res

    @property
    def _schema_set_packaging_dimension(self):
        return {
            "picking": {"type": "dict", "schema": self.schemas.picking()},
            "selected_move_line": {"type": "dict", "schema": self.schemas.move_line()},
            "packaging": {
                "type": "dict",
                "schema": self.schemas_detail.packaging_detail(),
            },
        }
