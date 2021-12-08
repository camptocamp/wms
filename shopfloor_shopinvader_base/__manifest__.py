# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopfloor / Shopinvader integration",
    "summary": "Provides base integration for Shopinvader into Shopfloor mobile app",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "E-commerce",
    "website": "https://github.com/OCA/wms",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainer": ["simahawk"],
    "license": "AGPL-3",
    "depends": ["shopfloor_base", "shopinvader", "sales_team"],
    "data": ["views/shopfloor_app.xml"],
    "demo": [
        "demo/tech_user_demo.xml",
        "demo/res_users_demo.xml",
        "demo/shopfloor_app_demo.xml",
    ],
}
