# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from .test_delivery_shipment_base import DeliveryShipmentCommonCase


class DeliveryShipmentScanDocumentCase(DeliveryShipmentCommonCase):
    """Tests for '/scan_document' endpoint."""

    def test_scan_document_barcode_not_found(self):
        response = self.service.dispatch(
            "scan_document",
            params={"shipment_advice_id": self.shipment.id, "barcode": "UNKNOWN"},
        )
        self.assert_response_scan_document(
            response, self.shipment, message=self.service.msg_store.barcode_not_found(),
        )

    def test_scan_document_shipment_planned_with_picking_not_planned(self):
        """Scan a delivery not planned in the shipment advice.

        The shipment advice has some deliveries planned but the user scans an
        unrelated one, returning an error.
        """
        self._plan_records_in_shipment(self.shipment, self.picking1 | self.picking2)
        response = self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": self.picking3.name,
            },
        )
        self.assert_response_scan_document(
            response,
            self.shipment,
            message=self.service.msg_store.picking_not_planned_in_shipment(
                self.picking3, self.shipment
            ),
        )

    def test_scan_document_shipment_planned_with_picking_planned(self):
        """Scan a delivery planned in the shipment advice.

        The shipment advice has some deliveries planned and the user scans an
        expected one, returning the planned content of this delivery for the
        current shipment.
        """
        self._plan_records_in_shipment(self.shipment, self.picking1)
        response = self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": self.picking1.name,
            },
        )
        self.assert_response_scan_document(
            response, self.shipment, self.picking1,
        )
        # Check returned content
        location_src = self.picking_type.default_location_src_id.name
        content = response["data"]["scan_document"]["content"]
        self.assertIn(location_src, content)
        #   'move_lines' key contains the only one product without package
        self.assertEqual(
            content[location_src]["move_lines"],
            self.service.data.move_lines(self.picking1.move_line_ids_without_package),
        )
        #   'package_levels' key contains the packages
        self.assertEqual(
            content[location_src]["package_levels"],
            self.service.data.package_levels(self.picking1.package_level_ids),
        )

    def test_scan_document_picking_with_unrelated_carrier(self):
        """Scan a delivery whose the carrier doesn't belong to the related
        carriers of the shipment (if any).

        This is only relevant for shipment without planned content.
        """
        self.picking1.carrier_id = self.env.ref("delivery.delivery_carrier")
        self.picking2.carrier_id = self.env.ref("delivery.normal_delivery_carrier")
        # Load the first delivery in the shipment
        self.picking1._load_in_shipment(self.shipment)
        # Scan the second which has a different carrier => error
        response = self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": self.picking2.name,
            },
        )
        self.assert_response_scan_document(
            response,
            self.shipment,
            message=self.service.msg_store.carrier_not_allowed_by_shipment(
                self.picking2
            ),
        )
