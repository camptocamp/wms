# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


import logging

from odoo import _
from odoo.exceptions import MissingError

from odoo.addons.component.core import Component
from odoo.addons.shopinvader.utils import get_partner_work_context

_logger = logging.getLogger(__name__)


class ShopfloorInvaderServiceContextProvider(Component):
    _name = "shopfloor.invader.service.context.provider"
    _inherit = "base.rest.service.context.provider"
    # No need to inherit from default ctx provider as it's all custom here
    # _inherit = "shopinvader.service.context.provider"
    _collection = "shopinvader.backend"
    _usage = "shopfloor_invader_component_context_provider"

    def _get_component_context(self):
        assert self.collection._name == self._collection
        res = super()._get_component_context()
        res.update(
            {
                "shopinvader_backend": self.collection,
                "shopinvader_session": self._get_shopinvader_session(),
            }
        )
        res.update(get_partner_work_context(self._get_shopinvader_partner()))
        return res

    def _get_shopinvader_partner(self):
        # As we use authenticated users the partner must come from current user.
        # NOTE: this piece could probably go into a new shopinvader module
        # but we want take full control on this ctx provider now.
        partner_model = self.env["shopinvader.partner"]
        # TODO: this could depend on having real users or not.
        # For now, we rely on having a real user in Odoo.
        partner = self.env.user.partner_id
        s_partner = partner._get_invader_partner(self.collection)
        if s_partner:
            return s_partner
        else:
            _logger.warning("Cannot determine shopinvader.partner")
            raise MissingError(_("The given shopinvader user is not found!"))
        return partner_model.browse()

    def _get_shopinvader_session(self):
        # HTTP_SESS are data that are store in the shopinvader session
        # and forwarded to odoo at each request
        # it allow to access to some specific field of the user session
        # By security always force typing
        # Note: rails cookies store session are serveless ;)
        return {
            "cart_id": int(self.request.httprequest.environ.get("HTTP_SESS_CART_ID", 0))
        }
