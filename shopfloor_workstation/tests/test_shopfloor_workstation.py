# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopfloor.tests.common import CommonCase


class ShopfloorWorkstationCase(CommonCase):
    def setUp(self):
        super().setUp()
        with self.work_on_services() as work:
            self.service = work.component(usage="workstation")

        self.pserver = self.env["printing.server"].sudo().create({})
        printer_vals = {
            "name": "P-One",
            "server_id": self.pserver.id,
            "system_name": "Sys Name",
            "default": True,
            "status": "unknown",
            "status_message": "Msg",
            "model": "res.users",
            "location": "Location",
            "uri": "URI",
        }
        self.printer1 = self.env["printing.printer"].sudo().create(printer_vals)
        printer_vals["name"] = "P-Two"
        self.printer2 = self.env["printing.printer"].sudo().create(printer_vals)
        self.ws1 = self.env.ref("shopfloor_workstation.ws_pollux")
        self.ws1.sudo().printing_printer_id = self.printer1
        self.profile1 = self.env.ref("shopfloor.shopfloor_profile_hb_truck_demo")
        self.ws1.sudo().shopfloor_profile_id = self.profile1

    def test_workstation_set_default_not_found(self):
        res = self.service.dispatch("setdefault", params={"barcode": "bc-???"})
        self.assert_response(
            res,
            message={"body": "Workstation not found", "message_type": "error",},
            data={"size": 0, "records": [],},
        )

    def test_workstation_set_default_found(self):
        self.assertFalse(self.env.user.printing_printer_id)
        res = self.service.dispatch("setdefault", params={"barcode": "ws-1"})
        self.assert_response(
            res,
            message={
                "body": "Default workstation set to Pollux",
                "message_type": "info",
            },
            data={
                "size": 1,
                "records": [
                    {
                        "id": self.ws1.id,
                        "name": "Pollux",
                        "barcode": "ws-1",
                        "profile": {
                            "id": self.ws1.shopfloor_profile_id.id,
                            "name": "Highbay Truck",
                        },
                    },
                ],
            },
        )
        self.assertEqual(self.env.user.printing_printer_id, self.printer1)
