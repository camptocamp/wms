# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Shopfloor Dangerous Goods",
    "summary": "Glue Module Between Shopfloor and l10n_eu_product_adr",
    "version": "13.0.1.0.0",
    "development_status": "Alpha",
    "category": "Inventory",
    "website": "https://github.com/OCA/wms",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["mmequignon"],
    "license": "AGPL-3",
    "application": True,
    "depends": [
        "shopfloor",
        # OCA/community-data-files
        "l10n_eu_product_adr",
    ],
    "data": [],
}
