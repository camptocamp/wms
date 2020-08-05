# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Delivery carrier dangerous goods warning",
    "summary": "Display dangerous goods warning according to delivery carrier",
    "version": "13.0.1.1.0",
    "development_status": "Alpha",
    "category": "Operations/Inventory/Delivery",
    "website": "https://github.com/OCA/wms",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["delivery", "l10n_eu_product_adr"],
    "data": [
        "views/delivery_carrier.xml",
        "views/sale_order.xml",
        "views/stock_picking.xml",
        "wizard/choose_delivery_carrier.xml",
    ],
}
