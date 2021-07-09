# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from .test_delivery_shipment_base import DeliveryShipmentCommonCase


class DeliveryShipmentLoadingListCase(DeliveryShipmentCommonCase):
    """Tests for '/loading_list' endpoint."""

    def test_loading_list_wrong_id(self):
        response = self.service.dispatch(
            "loading_list", params={"shipment_advice_id": -1}
        )
        self.assert_response_scan_dock(
            response, message=self.service.msg_store.record_not_found()
        )

    def test_loading_list_shipment_planned_partially_loaded(self):
        response = self.service.dispatch(
            "loading_list", params={"shipment_advice_id": self.shipment.id}
        )
        self.assert_response_loading_list(response, self.shipment)
        # Check returned content
        # TODO

    def test_loading_list_shipment_planned_fully_loaded(self):
        response = self.service.dispatch(
            "loading_list", params={"shipment_advice_id": self.shipment.id}
        )
        self.assert_response_loading_list(response, self.shipment)
        # Check returned content
        # TODO

    def test_loading_list_shipment_not_planned_partially_loaded(self):
        response = self.service.dispatch(
            "loading_list", params={"shipment_advice_id": self.shipment.id}
        )
        self.assert_response_loading_list(response, self.shipment)
        # Check returned content
        # TODO

    def test_loading_list_shipment_not_planned_fully_loaded(self):
        response = self.service.dispatch(
            "loading_list", params={"shipment_advice_id": self.shipment.id}
        )
        self.assert_response_loading_list(response, self.shipment)
        # Check returned content
        # TODO
