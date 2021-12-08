# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# @author: simone.orsi@camptocamp.com
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.addons.component.core import Component

# TODO: this is something I mande in 2019 in the ctx of a PoC for COS
# here https://github.com/camptocamp/odoo-shopinvader/
# tree/add-shopinvader_rest_product/shopinvader_rest_product
# should be moved to its own module in odoo-shopinvader if we keep it.


class ProductService(Component):
    _inherit = "base.shopinvader.service"
    _name = "shopinvader.product.service"
    _usage = "products"
    _expose_model = "shopinvader.variant"

    @property
    def _exposed_model(self):
        # TODO: do we care at all about permissions here?
        # I think not. This is correct till we access product info properly.
        # It would be better probably to have a specific RR?
        return super()._exposed_model.sudo()

    # The following method are 'public' and can be called from the controller.
    def get(self, _id):
        return self._to_json(self._get(_id))[0]

    def search(self, **params):
        return self._paginate_search(**params)

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _get(self, _id):
        return self.env[self._expose_model].browse(_id)

    def _to_json(self, records):
        # TODO: not super-efficient w/ many records
        return [rec._get_shop_data() for rec in records]

    # Validator
    def _validator_get(self):
        return {}

    def _validator_search(self):
        validator = self._default_validator_search()
        return validator
