# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
{
    "name": "Stock Warehouse Flow",
    "summary": "Configure routing flow for stock moves",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/wms",
    "category": "Warehouse Management",
    "version": "14.0.1.0.0",
    "license": "LGPL-3",
    "depends": ["stock", "delivery"],
    "demo": [],
    "data": ["security/ir.model.access.csv", "views/stock_warehouse_flow.xml"],
    "installable": True,
    "development_status": "Alpha",
}
