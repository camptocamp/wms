# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopfloor / Shopinvader integration - mobile",
    "summary": "Provides base integration for Shopinvader into Shopfloor mobile app",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "E-commerce",
    "website": "https://github.com/OCA/wms",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainer": ["simahawk"],
    "license": "AGPL-3",
    "depends": [
        "shopfloor_shopinvader_base",
        "shopfloor_mobile_base",
        # Needed because we assume we have real odoo users
        "shopfloor_mobile_base_auth_user",
    ],
    "data": ["templates/assets.xml"],
}
