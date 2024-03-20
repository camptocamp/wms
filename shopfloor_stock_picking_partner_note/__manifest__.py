# Copyright 2021 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Shopfloor Stock Picking Partner Note",
    "summary": "Adapts Shopfloor to Module stock_picking_partner_note",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Inventory",
    "website": "https://github.com/OCA/wms",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "depends": ["shopfloor", "stock_picking_partner_note"],
    "data": ["templates/assets.xml"],
    "auto_install": True,
}
