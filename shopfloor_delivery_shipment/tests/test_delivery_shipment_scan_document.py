# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from .test_delivery_shipment_base import DeliveryShipmentCommonCase


class DeliveryShipmentScanDocumentCase(DeliveryShipmentCommonCase):
    """Tests for '/scan_document' endpoint."""

    def test_scan_document_barcode_not_found(self):
        # TODO
        pass
        # response = self.service.dispatch("scan_dock", params={"barcode": "UNKNOWN"})
        # self.assert_response_scan_dock(
        #     response,
        #     message=self.service.msg_store.barcode_not_found(),
        # )

    def test_scan_document_ok(self):
        # TODO
        pass
