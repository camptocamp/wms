# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models

from odoo.addons.component.core import _component_databases

from ..controllers.main import ShopfloorInvaderController


class ShopfloorApp(models.Model):
    _inherit = "shopfloor.app"

    shopinvader_backend_id = fields.Many2one(
        comodel_name="shopinvader.backend",
        string="Shopinvader Backend",
    )

    shop_api_route = fields.Char(compute="_compute_shop_api_route")

    def _register_endpoints(self):
        super()._register_endpoints()
        self._register_shop_endpoints()

    def _register_shop_endpoints(self):
        services = self._get_shop_services()
        for service in services:
            self._prepare_non_decorated_endpoints(service)
            self._generate_shop_endpoints(service)
        self.env["rest.service.registration"]._register_rest_route(self.shop_api_route)

    def _is_component_registry_ready(self):
        # TODO: this can be moved to shopfloor_base
        comp_registry = _component_databases.get(self.env.cr.dbname)
        return comp_registry and comp_registry.ready

    def _get_shop_services(self):
        return self.env["rest.service.registration"]._get_services(
            "shopinvader.backend"
        )

    @api.depends("api_route")
    def _compute_shop_api_route(self):
        for rec in self:
            rec.shop_api_route = rec.api_route.rstrip("/") + "/invader/"

    def _generate_shop_endpoints(self, service):
        values = self._generate_endpoints_values(service, self.shop_api_route)
        rest_endpoint_handler = ShopfloorInvaderController()._process_method
        for vals in values:
            self._generate_endpoints_routes(service, rest_endpoint_handler, vals)
