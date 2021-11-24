# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.addons.shopfloor_mobile_base.controllers.main import (
    ShopfloorMobileAppController,
)


class ShopfloorMobileAppControllerUser(ShopfloorMobileAppController):
    def _make_app_info(self, shopfloor_app=None, demo=False):
        info = super()._make_app_info(shopfloor_app=shopfloor_app, demo=demo)
        if shopfloor_app:
            info["shop_api_route"] = shopfloor_app.shop_api_route_public
        return info
