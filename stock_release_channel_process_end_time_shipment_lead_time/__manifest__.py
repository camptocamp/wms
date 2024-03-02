# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Release Channel Process End Date Shipment Lead Time",
    "summary": """
        Glue module to compute what is releasable
        when there is a lead time and process end date""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "maintainers": ["jbaudoux"],
    "author": "BCIM, Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/wms",
    "depends": [
        "stock_release_channel_shipment_lead_time",
        "stock_release_channel_process_end_time",
    ],
    "auto_install": True,
}
