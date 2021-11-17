# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo.addons.base_rest.controllers import main

_logger = logging.getLogger(__name__)


class ShopfloorInvaderController(main.RestController):

    # TODO: this should be controlled from shopfloor.app ?
    # We should probably generate other app-specific URLs via app._generate_endpoints
    _component_context_provider = "shopfloor_invader_component_context_provider"

    def _process_method(
        self, service_name, method_name, *args, collection=None, params=None
    ):
        assert collection._name == "shopfloor.app"
        # get shopinvader backend from current app
        shopinvader_backend = collection.shopinvader_backend_id
        if not shopinvader_backend:
            # A not found will be raised later, just leave a trace for the poor devs :)
            _logger.error(
                "No shopinvader backend found for collection: %s", str(collection)
            )
        return super()._process_method(
            service_name,
            method_name,
            *args,
            collection=shopinvader_backend,
            params=params
        )
