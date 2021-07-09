# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from .test_delivery_shipment_base import DeliveryShipmentCommonCase


class DeliveryShipmentScanDocumentLotCase(DeliveryShipmentCommonCase):
    """Tests for '/scan_document' endpoint when scanning a lot."""

    def test_scan_document_shipment_planned_lot_not_planned(self):
        """Scan a lot not planned in the shipment advice.

        The shipment advice has some content planned but the user scans an
        unrelated one, returning an error.
        """
        self._plan_records_in_shipment(self.shipment, self.picking1.move_lines)
        scanned_lot = self.picking2.move_ids_without_package.move_line_ids.lot_id
        response = self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": scanned_lot.name,
            },
        )
        self.assert_response_scan_document(
            response,
            self.shipment,
            message=self.service.msg_store.lot_not_planned_in_shipment(
                scanned_lot, self.shipment
            ),
        )

    def test_scan_document_shipment_planned_lot_planned(self):
        """Scan a lot planned in the shipment advice.

        The shipment advice has some content planned and the user scans an
        expected one, loading the lot and returning the planned content
        of this delivery for the current shipment.
        """
        move_line = self.picking1.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_c
        )
        self._plan_records_in_shipment(self.shipment, move_line.move_id)
        scanned_lot = move_line.lot_id
        response = self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": scanned_lot.name,
            },
        )
        self.assert_response_scan_document(response, self.shipment, self.picking1)
        # Check lot status
        self.assertEqual(move_line.qty_done, move_line.product_uom_qty)
        # Check returned content
        location_src = self.picking_type.default_location_src_id.name
        content = response["data"]["scan_document"]["content"]
        self.assertIn(location_src, content)
        #   'move_lines' key contains the lot scanned
        self.assertEqual(
            content[location_src]["move_lines"],
            self.service.data.move_lines(move_line),
        )
        #   'package_levels' key doesn't exist (not planned for this shipment)
        self.assertNotIn("package_levels", content[location_src])

    def test_scan_document_shipment_not_planned_lot_not_planned(self):
        """Scan a lot not planned for a shipment not planned.

        Load the lot and return the available content to load/unload
        of the related delivery.
        """
        move_line = self.picking1.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_c
        )
        scanned_lot = move_line.lot_id
        response = self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": scanned_lot.name,
            },
        )
        self.assert_response_scan_document(response, self.shipment, self.picking1)
        # Check lot status
        self.assertEqual(move_line.qty_done, move_line.product_uom_qty)
        # Check returned content
        location_src = self.picking_type.default_location_src_id.name
        content = response["data"]["scan_document"]["content"]
        self.assertIn(location_src, content)
        #   'move_lines' key contains the lot scanned and other lines not yet
        # loaded from the same delivery
        self.assertEqual(
            content[location_src]["move_lines"],
            self.service.data.move_lines(
                self.picking1.move_ids_without_package.move_line_ids
            ),
        )
        #   'package_levels' key contains the package available from the same delivery
        self.assertEqual(
            content[location_src]["package_levels"],
            self.service.data.package_levels(self.picking1.package_level_ids),
        )

    def test_scan_document_shipment_not_planned_lot_not_planned_twice(self):
        """Scan a lot not planned twice for a shipment not planned.

        The second time a lot is scanned should not change anything: it has
        already been loaded during the first scan, the second scan returns
        the available content to load/unload of the related delivery.
        """
        move_line = self.picking1.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_c
        )
        scanned_lot = move_line.lot_id
        # First scan
        self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": scanned_lot.name,
            },
        )
        # Second scan
        response = self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": scanned_lot.name,
            },
        )
        self.assert_response_scan_document(response, self.shipment, self.picking1)
        # Check lot status
        self.assertEqual(move_line.qty_done, move_line.product_uom_qty)
        # Check returned content
        location_src = self.picking_type.default_location_src_id.name
        content = response["data"]["scan_document"]["content"]
        self.assertIn(location_src, content)
        #   'move_lines' key contains the lot scanned and other lines not yet
        # loaded from the same delivery
        self.assertEqual(
            content[location_src]["move_lines"],
            self.service.data.move_lines(
                self.picking1.move_ids_without_package.move_line_ids
            ),
        )
        #   'package_levels' key contains the package available from the same delivery
        self.assertEqual(
            content[location_src]["package_levels"],
            self.service.data.package_levels(self.picking1.package_level_ids),
        )

    def test_scan_document_shipment_not_planned_lot_planned(self):
        """Scan an already planned lot in the shipment not planned.

        Returns an error saying that the lot could not be loaded.
        """
        move_line = self.picking1.move_ids_without_package.move_line_ids
        scanned_lot = move_line.lot_id
        # Plan the lot in a another shipment
        new_shipment = self._create_shipment()
        self._plan_records_in_shipment(new_shipment, move_line.move_id)
        # Scan the lot: an error is returned as this lot has already
        # been planned in another shipment
        response = self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": scanned_lot.name,
            },
        )
        self.assert_response_scan_document(
            response,
            self.shipment,
            message=self.service.msg_store.unable_to_load_lot_in_shipment(
                scanned_lot, self.shipment
            ),
        )
