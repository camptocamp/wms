# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from .test_delivery_shipment_base import DeliveryShipmentCommonCase


class DeliveryShipmentScanDocumentProductCase(DeliveryShipmentCommonCase):
    """Tests for '/scan_document' endpoint when scanning a product."""

    def test_scan_document_shipment_planned_product_not_planned(self):
        """Scan a product not planned in the shipment advice.

        The shipment advice has some content planned but the user scans an
        unrelated one, returning an error.
        """
        planned_move = self.picking1.move_lines.filtered(
            lambda m: m.product_id == self.product_c
        )
        self._plan_records_in_shipment(self.shipment, planned_move)
        scanned_product = self.product_d
        response = self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": scanned_product.barcode,
            },
        )
        self.assert_response_scan_document(
            response,
            self.shipment,
            message=self.service.msg_store.product_not_planned_in_shipment(
                scanned_product, self.shipment
            ),
        )

    def test_scan_document_shipment_planned_product_planned(self):
        """Scan a product planned in the shipment advice.

        The shipment advice has some content planned and the user scans an
        expected one, loading the product and returning the planned content
        of this delivery for the current shipment.
        """
        move_line = self.picking1.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_d
        )
        self._plan_records_in_shipment(self.shipment, move_line.move_id)
        scanned_product = move_line.product_id
        response = self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": scanned_product.barcode,
            },
        )
        self.assert_response_scan_document(response, self.shipment, self.picking1)
        # Check product line status
        self.assertEqual(move_line.qty_done, move_line.product_uom_qty)
        # Check returned content
        location_src = self.picking_type.default_location_src_id.name
        content = response["data"]["scan_document"]["content"]
        self.assertIn(location_src, content)
        #   'move_lines' key contains the product scanned
        self.assertEqual(
            content[location_src]["move_lines"],
            self.service.data.move_lines(move_line),
        )
        #   'package_levels' key doesn't exist (not planned for this shipment)
        self.assertNotIn("package_levels", content[location_src])

    def test_scan_document_shipment_not_planned_product_not_planned(self):
        """Scan a product not planned for a shipment not planned.

        Load the product and return the available content to load/unload
        of the related delivery.
        """
        move_line = self.picking1.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_d
        )
        scanned_product = move_line.product_id
        response = self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": scanned_product.barcode,
            },
        )
        self.assert_response_scan_document(response, self.shipment, self.picking1)
        # Check product line status
        self.assertEqual(move_line.qty_done, move_line.product_uom_qty)
        # Check returned content
        location_src = self.picking_type.default_location_src_id.name
        content = response["data"]["scan_document"]["content"]
        self.assertIn(location_src, content)
        #   'move_lines' key contains the product scanned and other lines not
        # yet loaded from the same delivery
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

    def test_scan_document_shipment_not_planned_product_not_planned_twice(self):
        """Scan a product not planned twice for a shipment not planned.

        The second time a product is scanned should not change anything: it has
        already been loaded during the first scan, the second scan returns
        the available content to load/unload of the related delivery.
        """
        move_line = self.picking1.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_d
        )
        scanned_product = move_line.product_id
        # First scan
        self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": scanned_product.barcode,
            },
        )
        # Second scan
        response = self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": scanned_product.barcode,
            },
        )
        self.assert_response_scan_document(response, self.shipment, self.picking1)
        # Check product line status
        self.assertEqual(move_line.qty_done, move_line.product_uom_qty)
        # Check returned content
        location_src = self.picking_type.default_location_src_id.name
        content = response["data"]["scan_document"]["content"]
        self.assertIn(location_src, content)
        #   'move_lines' key contains the product scanned and other lines not
        # yet loaded from the same delivery
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

    def test_scan_document_shipment_not_planned_product_planned(self):
        """Scan an already planned product in the shipment not planned.

        Returns an error saying that the product could not be loaded.
        """
        # Grab all lines related to product to plan
        move_lines = self.pickings.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_d
        )
        scanned_product = self.product_d
        # Plan all the product moves in a another shipment
        new_shipment = self._create_shipment()
        self._plan_records_in_shipment(new_shipment, move_lines.move_id)
        # Scan the product: an error is returned as these product lines have
        # already been planned in another shipment
        response = self.service.dispatch(
            "scan_document",
            params={
                "shipment_advice_id": self.shipment.id,
                "barcode": scanned_product.barcode,
            },
        )
        self.assert_response_scan_document(
            response,
            self.shipment,
            message=self.service.msg_store.unable_to_load_product_in_shipment(
                scanned_product, self.shipment
            ),
        )
