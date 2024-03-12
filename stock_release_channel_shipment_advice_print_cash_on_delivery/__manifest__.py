# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Release Channel Shipment Advice Print Cash on Delivery",
    "summary": """This module allows users to print cash on delivery invoices
    from a release channel and a shipment advice""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/wms",
    "depends": ["sale_stock", "account", "stock_release_channel_shipment_advice"],
    "data": [
        "views/account_payment_term_views.xml",
        "views/shipment_advice.xml",
        "views/stock_picking_views.xml",
        "views/stock_release_channel.xml",
    ],
}
