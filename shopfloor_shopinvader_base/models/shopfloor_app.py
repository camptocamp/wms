# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models

from ..controllers.main import ShopfloorInvaderController


class ShopfloorApp(models.Model):
    _inherit = "shopfloor.app"

    category = fields.Selection(selection_add=[("shop", "Shop")])
    shopinvader_backend_id = fields.Many2one(
        comodel_name="shopinvader.backend",
        string="Shopinvader Backend",
    )
    shopinvader_tech_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Shopinvader Tech User",
        help="""
        If this user is not set,
        you'll have to ensure that every app user calling shop services
        is allowed to handle sale records (eg: sale.order write).
        """,
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
        for vals in values:
            rest_endpoint_handler = (
                ShopfloorInvaderController()._process_shopinvader_endpoint
            )
            self._generate_endpoints_routes(service, rest_endpoint_handler, vals)
